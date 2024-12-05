import 'dart:convert';
import 'package:http/http.dart' as http;

class AdvisoryService {
  static Future<Map<String, dynamic>> fetchHealthAdvisory(
      String globalCity, String user_id) async {
    final String xmlData = '''
      <request>
        <city>$globalCity</city>
        <user_id>$user_id</user_id>
      </request>
    ''';

    final response = await http.post(
      Uri.parse('http://192.168.1.9:5002/get_health_advisory'),
      headers: {'Content-Type': 'application/xml'},
      body: xmlData,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> advisory = json.decode(response.body);
      return advisory;
    } else {
      throw Exception('Failed to load health advisory');
    }
  }
}
