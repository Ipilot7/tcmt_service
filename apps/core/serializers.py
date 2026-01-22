from typing import Dict, Any
from .models import Institution, Equipment

class InstitutionSerializer:
    """
    Serializer for Institution model.
    Handles transformation from model instance to dictionary.
    """
    
    @staticmethod
    def serialize(institution: Institution) -> Dict[str, Any]:
        return {
            'id': institution.id,
            'name': institution.name,
            'region_id': institution.region_id,
            'region_name': institution.region.name if institution.region else None,
            'sale_date': institution.sale_date.strftime('%Y-%m-%d') if institution.sale_date else None,
            'warranty_end': institution.warranty_end.strftime('%Y-%m-%d') if institution.warranty_end else None,
            'is_under_warranty': institution.is_under_warranty,
            'equipments': EquipmentSerializer.serialize_list(institution.equipments.all()),
        }

    @staticmethod
    def serialize_list(institutions) -> list:
        return [InstitutionSerializer.serialize(inst) for inst in institutions]

class EquipmentSerializer:
    """
    Serializer for Equipment model.
    """
    
    @staticmethod
    def serialize(equipment: Equipment) -> Dict[str, Any]:
        inst = equipment.institutions.first()
        return {
            'id': equipment.id,
            'equipment_type_id': equipment.equipment_type_id,
            'equipment_type_name': equipment.equipment_type.name if equipment.equipment_type else None,
            'serial_number': equipment.serial_number,
            'institution_name': inst.name if inst else None,
            'warranty_end': inst.warranty_end.strftime('%Y-%m-%d') if inst and inst.warranty_end else None,
            'is_under_warranty': inst.is_under_warranty if inst else False,
        }

    @staticmethod
    def serialize_list(equipments) -> list:
        return [EquipmentSerializer.serialize(eq) for eq in equipments]
