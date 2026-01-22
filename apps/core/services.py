from .models import Institution, Equipment
from .serializers import InstitutionSerializer, EquipmentSerializer

def institution_create(*, name, region, sale_date=None, equipments=None) -> dict:
    """
    Creates a new institution and returns serialized data.
    """
    institution = Institution(name=name, region=region, sale_date=sale_date)
    institution.full_clean()
    institution.save()
    if equipments:
        institution.equipments.set(equipments)
    return InstitutionSerializer.serialize(institution)

def institution_update(*, institution: Institution, name, region, sale_date=None, equipments=None) -> dict:
    """
    Updates an existing institution and returns serialized data.
    """
    institution.name = name
    institution.region = region
    institution.sale_date = sale_date
    institution.full_clean()
    institution.save()
    if equipments is not None:
        institution.equipments.set(equipments)
    return InstitutionSerializer.serialize(institution)

def equipment_create(*, equipment_type, serial_number) -> dict:
    """
    Creates a new equipment and returns serialized data.
    """
    equipment = Equipment(
        equipment_type=equipment_type, 
        serial_number=serial_number
    )
    equipment.full_clean()
    equipment.save()
    return EquipmentSerializer.serialize(equipment)

def equipment_update(*, equipment: Equipment, equipment_type, serial_number) -> dict:
    """
    Updates an existing equipment and returns serialized data.
    """
    equipment.equipment_type = equipment_type
    equipment.serial_number = serial_number
    equipment.full_clean()
    equipment.save()
    return EquipmentSerializer.serialize(equipment)
