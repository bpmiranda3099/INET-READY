import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:inet_ready_app/src/screens/home.dart';

class Authentication {
  static Future<void> signIn(
      BuildContext context, String email, String password) async {
    final String xmlData = '''
      <login>
        <username>$email</username>
        <password>$password</password>
      </login>
    ''';

    final response = await http.post(
      Uri.parse('http://192.168.1.9:5001/sign_in'),
      headers: {'Content-Type': 'application/xml'},
      body: xmlData,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> responseData = json.decode(response.body);
      if (responseData['status'] == 'success') {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => HomeScreen()),
        );
      } else {
        _showErrorDialog(context, 'Invalid credentials');
      }
    } else {
      _showErrorDialog(context, 'Error connecting to server');
    }
  }

  static void _showErrorDialog(BuildContext context, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Error'),
        content: Text(message),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }
}
