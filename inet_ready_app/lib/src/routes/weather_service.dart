import 'dart:convert';
import 'package:http/http.dart' as http;

class WeatherService {
  static Future<List<String>> fetchCities() async {
    final response = await http.get(
      Uri.parse('http://192.168.1.9:5000/get_cities'),
      headers: {'Content-Type': 'application/xml'},
    );

    if (response.statusCode == 200) {
      final List<String> cities = List<String>.from(json.decode(response.body));
      return cities;
    } else {
      throw Exception('Failed to load cities');
    }
  }

  static Future<Map<String, dynamic>> fetchCurrentWeather(String city) async {
    final String xmlData = '''
      <request>
        <city>$city</city>
      </request>
    ''';

    final response = await http.post(
      Uri.parse('http://192.168.1.9:5000/get_current_weather'),
      headers: {'Content-Type': 'application/xml'},
      body: xmlData,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> currentWeather = json.decode(response.body);
      return currentWeather;
    } else {
      throw Exception('Failed to load current weather');
    }
  }

  static Future<List<Map<String, dynamic>>> fetchForecast(String city) async {
    final String xmlData = '''
      <request>
        <city>$city</city>
      </request>
    ''';

    final response = await http.post(
      Uri.parse('http://192.168.1.9:5000/get_forecast'),
      headers: {'Content-Type': 'application/xml'},
      body: xmlData,
    );

    if (response.statusCode == 200) {
      final List<Map<String, dynamic>> forecast =
          List<Map<String, dynamic>>.from(json.decode(response.body));
      return forecast;
    } else {
      throw Exception('Failed to load forecast');
    }
  }
}
