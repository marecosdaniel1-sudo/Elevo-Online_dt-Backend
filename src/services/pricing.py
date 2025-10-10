"""
Servicio de cálculo de precios
Implementa la lógica de negocio para calcular costos de renta
"""
from typing import List, Dict
from datetime import datetime, timedelta

from src.core.config import settings
from src.models.order import RentalPeriod
from src.models.scaffold import Scaffold


class PricingService:
    """
    Servicio para calcular precios de renta de andamios
    """
    
    @staticmethod
    def calculate_rental_days(start_date: datetime, end_date: datetime) -> int:
        """
        Calcula el número de días de renta
        """
        delta = end_date - start_date
        return max(1, delta.days)
    
    @staticmethod
    def get_unit_price(scaffold: Scaffold, rental_period: RentalPeriod, days: int) -> float:
        """
        Obtiene el precio unitario basado en el periodo de renta
        
        Args:
            scaffold: Andamio a rentar
            rental_period: Periodo de renta (daily, weekly, monthly)
            days: Número de días de renta
        
        Returns:
            Precio por unidad para el periodo completo
        """
        if rental_period == RentalPeriod.DAILY:
            return scaffold.daily_rate * days
        
        elif rental_period == RentalPeriod.WEEKLY:
            weeks = max(1, days // 7)
            remaining_days = days % 7
            return (scaffold.weekly_rate * weeks) + (scaffold.daily_rate * remaining_days)
        
        elif rental_period == RentalPeriod.MONTHLY:
            months = max(1, days // 30)
            remaining_days = days % 30
            return (scaffold.monthly_rate * months) + (scaffold.daily_rate * remaining_days)
        
        else:  # CUSTOM
            # Para custom, usamos la tarifa diaria
            return scaffold.daily_rate * days
    
    @staticmethod
    def calculate_discount(
        subtotal: float,
        rental_period: RentalPeriod,
        quantity: int,
        days: int
    ) -> Dict[str, float]:
        """
        Calcula descuentos aplicables
        
        Returns:
            Dict con discount_amount y discount_percentage
        """
        discount_percentage = 0.0
        
        # Descuento por periodo largo
        if rental_period == RentalPeriod.WEEKLY or days >= 7:
            discount_percentage = max(discount_percentage, settings.WEEKLY_DISCOUNT)
        
        if rental_period == RentalPeriod.MONTHLY or days >= 30:
            discount_percentage = max(discount_percentage, settings.MONTHLY_DISCOUNT)
        
        # Descuento por volumen
        if quantity >= settings.BULK_DISCOUNT_THRESHOLD:
            discount_percentage = max(discount_percentage, settings.BULK_DISCOUNT_RATE)
        
        # Descuento acumulativo si cumple ambas condiciones
        if quantity >= settings.BULK_DISCOUNT_THRESHOLD and days >= 30:
            discount_percentage = min(
                discount_percentage + 0.05,  # 5% adicional
                0.30  # Máximo 30% de descuento total
            )
        
        discount_amount = subtotal * discount_percentage
        
        return {
            "discount_amount": round(discount_amount, 2),
            "discount_percentage": discount_percentage
        }
    
    @staticmethod
    def calculate_delivery_fee(postal_code: str = None) -> float:
        """
        Calcula el costo de envío basado en código postal
        
        TODO: Implementar lógica más sofisticada con zonas geográficas
        """
        # Por ahora, tarifa fija
        # En el futuro, se puede integrar con API de geolocalización
        if postal_code is None:
            return settings.DELIVERY_FEE
        return settings.DELIVERY_FEE
    
    @staticmethod
    def calculate_tax(subtotal: float, discount: float) -> float:
        """
        Calcula impuestos (IVA 16% en México)
        """
        taxable_amount = subtotal - discount
        return round(taxable_amount * 0.16, 2)
    
    @staticmethod
    def calculate_deposit(scaffolds: List[tuple[Scaffold, int]]) -> float:
        """
        Calcula el depósito de garantía total
        
        Args:
            scaffolds: Lista de tuplas (scaffold, quantity)
        
        Returns:
            Monto total del depósito
        """
        total_deposit = 0.0
        for scaffold, quantity in scaffolds:
            total_deposit += scaffold.deposit_amount * quantity
        
        return round(total_deposit, 2)
    
    @classmethod
    def calculate_order_price(
        cls,
        items: List[Dict],  # [{scaffold: Scaffold, quantity: int}]
        start_date: datetime,
        end_date: datetime,
        rental_period: RentalPeriod,
        postal_code: str = None
    ) -> Dict:
        """
        Calcula el precio total de un pedido
        
        Returns:
            Dict con todos los cálculos de precio
        """
        days = cls.calculate_rental_days(start_date, end_date)
        
        # Calcular subtotal por item
        breakdown = []
        subtotal = 0.0
        total_quantity = 0
        scaffolds_for_deposit = []
        
        for item in items:
            scaffold = item['scaffold']
            quantity = item['quantity']
            
            unit_price = cls.get_unit_price(scaffold, rental_period, days)
            item_subtotal = unit_price * quantity
            
            breakdown.append({
                "scaffold_id": scaffold.id,
                "scaffold_name": scaffold.name,
                "quantity": quantity,
                "unit_price": round(unit_price, 2),
                "subtotal": round(item_subtotal, 2)
            })
            
            subtotal += item_subtotal
            total_quantity += quantity
            scaffolds_for_deposit.append((scaffold, quantity))
        
        subtotal = round(subtotal, 2)
        
        # Calcular descuentos
        discount_info = cls.calculate_discount(
            subtotal,
            rental_period,
            total_quantity,
            days
        )
        
        # Calcular delivery
        delivery_fee = cls.calculate_delivery_fee(postal_code)
        
        # Calcular impuestos
        tax_amount = cls.calculate_tax(subtotal, discount_info['discount_amount'])
        
        # Calcular depósito
        deposit_amount = cls.calculate_deposit(scaffolds_for_deposit)
        
        # Calcular total
        total_amount = (
            subtotal 
            - discount_info['discount_amount'] 
            + delivery_fee 
            + tax_amount
        )
        
        return {
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "discount_amount": discount_info['discount_amount'],
            "discount_percentage": discount_info['discount_percentage'],
            "tax_amount": tax_amount,
            "deposit_amount": deposit_amount,
            "total_amount": round(total_amount, 2),
            "rental_days": days,
            "breakdown": breakdown
        }
