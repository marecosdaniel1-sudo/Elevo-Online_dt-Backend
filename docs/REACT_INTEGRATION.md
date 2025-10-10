# 🔗 Integración con Frontend (React)

Guía completa para conectar un frontend React con Elevo Online API.

---

## 📋 Tabla de Contenidos

- [Configuración Inicial](#-configuración-inicial)
- [Autenticación](#-autenticación)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Componentes Útiles](#-componentes-útiles)
- [Manejo de Errores](#-manejo-de-errores)
- [Best Practices](#-best-practices)

---

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
npm install axios
# o
yarn add axios
```

### 2. Variables de Entorno

Crear archivo `.env` en la raíz del proyecto React:

```env
VITE_API_URL=http://localhost:8000/api/v1
# o para Create React App:
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3. Cliente HTTP Base

**`src/services/api.js`**
```javascript
import axios from 'axios';

// URL base de la API
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🔐 Autenticación

### Service de Autenticación

**`src/services/authService.js`**
```javascript
import api from './api';

const authService = {
  /**
   * Registrar nuevo usuario
   */
  async register(userData) {
    try {
      const response = await api.post('/auth/register', {
        email: userData.email,
        password: userData.password,
        full_name: userData.fullName,
        role: 'customer', // Por defecto
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Iniciar sesión
   */
  async login(email, password) {
    try {
      // La API espera form data
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, token_type, user } = response.data;

      // Guardar token y usuario en localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Cerrar sesión
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  /**
   * Obtener usuario actual
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Verificar si está autenticado
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Manejo de errores
   */
  handleError(error) {
    if (error.response) {
      // Error de la API
      return new Error(error.response.data.detail || 'Error en la operación');
    } else if (error.request) {
      // No hay respuesta
      return new Error('No se pudo conectar con el servidor');
    } else {
      return new Error('Error inesperado');
    }
  },
};

export default authService;
```

### Hook Personalizado de Autenticación

**`src/hooks/useAuth.js`**
```javascript
import { useState, useEffect, createContext, useContext } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay usuario guardado
    const savedUser = authService.getCurrentUser();
    if (savedUser) {
      setUser(savedUser);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    return data;
  };

  const register = async (userData) => {
    const data = await authService.register(userData);
    return data;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    isAuthenticated: authService.isAuthenticated(),
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};
```

### Componente de Login

**`src/pages/Login.jsx`**
```javascript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit}>
        <h2>Iniciar Sesión</h2>

        {error && <div className="error">{error}</div>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Iniciando...' : 'Entrar'}
        </button>
      </form>
    </div>
  );
};

export default Login;
```

### Ruta Protegida

**`src/components/ProtectedRoute.jsx`**
```javascript
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return <div>Cargando...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  // Verificar rol si se especifica
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};

export default ProtectedRoute;
```

**Uso en App.jsx:**
```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminPanel />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

---

## 🛒 Ejemplos de Uso

### Service de Andamios

**`src/services/scaffoldService.js`**
```javascript
import api from './api';

const scaffoldService = {
  /**
   * Obtener todos los andamios
   */
  async getAll(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('tipo', filters.type);
      if (filters.available) params.append('disponible', 'true');

      const response = await api.get(`/scaffolds?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Obtener andamio por ID
   */
  async getById(id) {
    try {
      const response = await api.get(`/scaffolds/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Calcular precio de renta
   */
  async calculatePrice(items, rentalPeriod, startDate, endDate) {
    try {
      const response = await api.post('/scaffolds/calculate-price', {
        items,
        rental_period: rentalPeriod,
        start_date: startDate,
        end_date: endDate,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  handleError(error) {
    if (error.response) {
      return new Error(error.response.data.detail || 'Error en la operación');
    }
    return new Error('Error de conexión');
  },
};

export default scaffoldService;
```

### Service de Órdenes

**`src/services/orderService.js`**
```javascript
import api from './api';

const orderService = {
  /**
   * Crear nueva orden
   */
  async create(orderData) {
    try {
      const response = await api.post('/orders', {
        items: orderData.items.map((item) => ({
          scaffold_id: item.scaffoldId,
          quantity: item.quantity,
        })),
        rental_period: orderData.rentalPeriod,
        start_date: orderData.startDate,
        end_date: orderData.endDate,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Obtener órdenes del usuario
   */
  async getMyOrders(status = null) {
    try {
      const params = status ? `?status=${status}` : '';
      const response = await api.get(`/orders${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Obtener orden por ID
   */
  async getById(id) {
    try {
      const response = await api.get(`/orders/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Confirmar orden (cliente)
   */
  async confirm(orderId) {
    try {
      const response = await api.post(`/orders/${orderId}/confirm`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  /**
   * Aprobar orden (admin)
   */
  async approve(orderId) {
    try {
      const response = await api.post(`/orders/${orderId}/approve`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  },

  handleError(error) {
    if (error.response) {
      return new Error(error.response.data.detail || 'Error en la operación');
    }
    return new Error('Error de conexión');
  },
};

export default orderService;
```

### Componente de Catálogo

**`src/components/ScaffoldCatalog.jsx`**
```javascript
import { useState, useEffect } from 'react';
import scaffoldService from '../services/scaffoldService';

const ScaffoldCatalog = ({ onAddToCart }) => {
  const [scaffolds, setScaffolds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState({ type: '', available: true });

  useEffect(() => {
    loadScaffolds();
  }, [filter]);

  const loadScaffolds = async () => {
    try {
      setLoading(true);
      const data = await scaffoldService.getAll(filter);
      setScaffolds(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="scaffold-catalog">
      {/* Filtros */}
      <div className="filters">
        <select value={filter.type} onChange={(e) => setFilter({ ...filter, type: e.target.value })}>
          <option value="">Todos los tipos</option>
          <option value="TUBULAR">Tubular</option>
          <option value="MULTIDIRECCIONAL">Multidireccional</option>
          <option value="COLGANTE">Colgante</option>
        </select>
      </div>

      {/* Lista de andamios */}
      <div className="scaffold-grid">
        {scaffolds.map((scaffold) => (
          <div key={scaffold.id} className="scaffold-card">
            <h3>{scaffold.name}</h3>
            <p>{scaffold.description}</p>
            <p>SKU: {scaffold.sku}</p>
            <p>Tipo: {scaffold.type}</p>
            <p>Disponibles: {scaffold.available_stock}</p>
            <div className="prices">
              <span>Día: ${scaffold.daily_rate}</span>
              <span>Semana: ${scaffold.weekly_rate}</span>
              <span>Mes: ${scaffold.monthly_rate}</span>
            </div>
            <button onClick={() => onAddToCart(scaffold)} disabled={scaffold.available_stock === 0}>
              {scaffold.available_stock > 0 ? 'Agregar al carrito' : 'No disponible'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScaffoldCatalog;
```

### Componente de Carrito

**`src/components/Cart.jsx`**
```javascript
import { useState } from 'react';
import orderService from '../services/orderService';
import scaffoldService from '../services/scaffoldService';

const Cart = ({ items, onUpdateQuantity, onRemove, onClear }) => {
  const [rentalPeriod, setRentalPeriod] = useState('DIARIO');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const calculateTotal = async () => {
    try {
      setLoading(true);
      const result = await scaffoldService.calculatePrice(
        items.map((item) => ({
          scaffold_id: item.id,
          quantity: item.quantity,
        })),
        rentalPeriod,
        startDate,
        endDate
      );
      setTotal(result.total);
    } catch (error) {
      console.error('Error calculando precio:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    try {
      setLoading(true);
      const order = await orderService.create({
        items: items.map((item) => ({
          scaffoldId: item.id,
          quantity: item.quantity,
        })),
        rentalPeriod,
        startDate,
        endDate,
      });
      
      alert(`Orden creada con éxito! ID: ${order.id}`);
      onClear();
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cart">
      <h2>Carrito de Compras</h2>

      {items.length === 0 ? (
        <p>El carrito está vacío</p>
      ) : (
        <>
          {/* Items */}
          <div className="cart-items">
            {items.map((item) => (
              <div key={item.id} className="cart-item">
                <h4>{item.name}</h4>
                <input
                  type="number"
                  min="1"
                  max={item.available_stock}
                  value={item.quantity}
                  onChange={(e) => onUpdateQuantity(item.id, parseInt(e.target.value))}
                />
                <button onClick={() => onRemove(item.id)}>Eliminar</button>
              </div>
            ))}
          </div>

          {/* Configuración de renta */}
          <div className="rental-config">
            <select value={rentalPeriod} onChange={(e) => setRentalPeriod(e.target.value)}>
              <option value="DIARIO">Diario</option>
              <option value="SEMANAL">Semanal</option>
              <option value="MENSUAL">Mensual</option>
            </select>

            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />

            <button onClick={calculateTotal} disabled={loading}>
              Calcular Total
            </button>
          </div>

          {/* Total */}
          {total > 0 && (
            <div className="cart-total">
              <h3>Total: ${total.toFixed(2)}</h3>
              <button onClick={handleCheckout} disabled={loading}>
                Finalizar Orden
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Cart;
```

---

## 🧩 Componentes Útiles

### Hook para Fetch de Datos

**`src/hooks/useFetch.js`**
```javascript
import { useState, useEffect } from 'react';

const useFetch = (fetchFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFunction();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, dependencies);

  const refetch = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch };
};

export default useFetch;
```

**Uso:**
```javascript
import useFetch from '../hooks/useFetch';
import scaffoldService from '../services/scaffoldService';

const ScaffoldList = () => {
  const { data: scaffolds, loading, error, refetch } = useFetch(
    () => scaffoldService.getAll(),
    []
  );

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <button onClick={refetch}>Recargar</button>
      {scaffolds.map((scaffold) => (
        <div key={scaffold.id}>{scaffold.name}</div>
      ))}
    </div>
  );
};
```

---

## ⚠️ Manejo de Errores

### Componente de Error Boundary

**`src/components/ErrorBoundary.jsx`**
```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>Algo salió mal</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>Recargar página</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Toast de Notificaciones

**Usando react-toastify:**
```bash
npm install react-toastify
```

**`src/utils/notifications.js`**
```javascript
import { toast } from 'react-toastify';

export const notify = {
  success: (message) => toast.success(message),
  error: (message) => toast.error(message),
  info: (message) => toast.info(message),
  warning: (message) => toast.warning(message),
};
```

**Uso:**
```javascript
import { notify } from '../utils/notifications';

const handleSubmit = async () => {
  try {
    await orderService.create(orderData);
    notify.success('Orden creada exitosamente');
  } catch (error) {
    notify.error(error.message);
  }
};
```

---

## ✅ Best Practices

### 1. Manejo de Tokens

```javascript
// ✅ Bueno: Usar interceptors de axios
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ❌ Malo: Agregar token manualmente en cada request
api.get('/orders', {
  headers: { Authorization: `Bearer ${token}` },
});
```

### 2. Validación de Formularios

```javascript
// ✅ Bueno: Validar antes de enviar
const validate = (data) => {
  const errors = {};
  if (!data.email.includes('@')) {
    errors.email = 'Email inválido';
  }
  if (data.password.length < 8) {
    errors.password = 'Mínimo 8 caracteres';
  }
  return errors;
};

// ❌ Malo: Confiar solo en validación del servidor
```

### 3. Loading States

```javascript
// ✅ Bueno: Mostrar feedback al usuario
const [loading, setLoading] = useState(false);

const handleSubmit = async () => {
  setLoading(true);
  try {
    await api.post('/orders', data);
  } finally {
    setLoading(false);
  }
};

return (
  <button disabled={loading}>
    {loading ? 'Procesando...' : 'Enviar'}
  </button>
);
```

### 4. Debounce en Búsquedas

```javascript
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

const SearchScaffolds = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  useEffect(() => {
    const debouncedSearch = debounce(async (searchQuery) => {
      if (searchQuery) {
        const data = await scaffoldService.search(searchQuery);
        setResults(data);
      }
    }, 500);

    debouncedSearch(query);

    return () => debouncedSearch.cancel();
  }, [query]);

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
};
```

### 5. Caché de Datos

```javascript
// Usar React Query para caché automático
import { useQuery } from '@tanstack/react-query';

const useScaffolds = () => {
  return useQuery({
    queryKey: ['scaffolds'],
    queryFn: scaffoldService.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};
```

---

## 🔧 Configuración CORS

El backend ya tiene CORS configurado para `http://localhost:3000` (React con CRA) y `http://localhost:5173` (Vite).

Si usas otro puerto, actualiza `src/core/config.py`:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4200",  # Angular
    "http://localhost:8080",  # Vue
]
```

---

## 📚 Recursos Adicionales

- **Documentación de la API**: http://localhost:8000/api/docs
- **React Router**: https://reactrouter.com/
- **Axios**: https://axios-http.com/
- **React Query**: https://tanstack.com/query/

---

**¡Listo para desarrollar tu frontend con React! 🚀**
