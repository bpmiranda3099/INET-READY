import 'package:xml/xml.dart' as xml;

Map<String, dynamic> data = {
  'user_id': null,
  'name': null,
  'username': null,
  'location': null,
  'demographics': {
    'age': null,
    'gender': null,
  },
  'biometrics': {
    'height': null,
    'weight': null,
  },
  'medical_conditions': {
    'cardiovascular_disease': null,
    'diabetes': null,
    'respiratory_issues': null,
    'heat_sensitivity': null,
    'kidney_disease': null,
    'neurological_disorders': null,
    'other_condition': null,
  },
  'medications': {
    'diuretics': null,
    'blood_pressure_medications': null,
    'antihistamines': null,
    'antidepressants': null,
    'antipsychotics': null,
    'other_medication': null,
  },
  'fluid_intake': {
    'water_amount': null,
    'electrolyte_drinks_amount': null,
    'coconut_water_amount': null,
    'fruit_juice_amount': null,
    'iced_tea_amount': null,
    'soda_amount': null,
    'milk_tea_amount': null,
    'coffee_amount': null,
    'herbal_tea_amount': null,
    'other_fluid': null,
    'other_fluid_amount': null,
  },
  'heat_conditions': {
    'mild_dehydration': null,
    'heat_rash': null,
    'heat_stroke': null,
    'muscle_fatigue': null,
    'heat_syncope': null,
    'heat_edema': null,
    'heat_exhaustion': null,
  },
  'activity': {
    'previous_heat_issues': null,
    'heat_issues_details': null,
    'outdoor_activity': null,
    'activity_level': null,
    'activity_duration': null,
  },
};

String generateXml(Map<String, dynamic> data) {
  final builder = xml.XmlBuilder();
  builder.processing('xml', 'version="1.0" encoding="UTF-8"');
  builder.element('UserData', nest: () {
    data.forEach((key, value) {
      if (value is Map) {
        builder.element(key, nest: () {
          value.forEach((subKey, subValue) {
            builder.element(subKey, nest: subValue?.toString() ?? '');
          });
        });
      } else {
        builder.element(key, nest: value?.toString() ?? '');
      }
    });
  });
  return builder.buildDocument().toString();
}

String xmlData = generateXml(data);
