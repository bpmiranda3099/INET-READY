import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: LoginScreen(),
    );
  }
}

class LoginScreen extends StatelessWidget {
  LoginScreen({super.key});

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login Screen'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Handle login logic
              },
              child: const Text('Login'),
            ),
            TextButton(
              onPressed: () {
                // Handle forgot password logic
              },
              child: const Text('Forgot Password?'),
            ),
            ElevatedButton(
              onPressed: () {
                // Handle login as guest logic
              },
              child: const Text('Login as Guest'),
            ),
            TextButton(
              onPressed: () {
                // Handle create account logic
              },
              child: const Text("Don't have an account? Create an account"),
            ),
          ],
        ),
      ),
    );
  }
}
