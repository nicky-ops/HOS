from datetime import timedelta
from .models import Driver


def calculate_hos_compliance(driver_id, distance, duration, current_cycle_used):
    '''
    Calculate HOS compliance for a trip
    '''
    driver = Driver.objects.get(pk=driver_id)

    # Calculate required breaks
    required_30_min_break = duration > 8
    required_rest_period = duration > 14

    # Calculate cycle limits
    if driver.cycle_type == '70/8':
        remaining_hours = 70 - current_cycle_used
    else:
        remaining_hours = 60 - current_cycle_used

    #  Check for violations
    violations = []
    if duration > 11:
        violations.append('Exceeds 11-hour driving limit')
    if duration > 14:
        violations.append('Exceeds 14-hour on-duty limit')
    if (current_cycle_used + duration) > (70 if driver.cycle_type == '70/8' else 60):
        violations.append('Exceeds weekly hour limit')

    return {
        'required_30_min_break': required_30_min_break,
        'required_rest_period': required_rest_period,
        'remaining_hours_in_cycle': remaining_hours,
        'violations': violations,
        'new_cycle_used': current_cycle_used + duration
    }