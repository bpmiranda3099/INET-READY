import 'package:flutter/material.dart';
import '/src/screens/sign_in.dart'; // Import the SignInScreen

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'INET-READY'), // Update title
      routes: {
        '/sign-in': (context) =>
            const SignInScreen(), // Add route for SignInScreen
      },
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Padding(
              padding: EdgeInsets.only(
                  top: 20.0, bottom: 60.0), // Add top and bottom padding
              child: Column(
                children: [
                  Text(
                    'INET-READY',
                    style: TextStyle(fontSize: 65), // Set the font size here
                  ),
                  Text(
                    'Your Heat Check for Safe and Informed Travel',
                    style: TextStyle(fontSize: 17), // Set the font size here
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          IconButton(
            icon: const Icon(Icons.login, size: 20), // Set the icon size here
            onPressed: () {
              Navigator.pushNamed(
                  context, '/sign-in'); // Navigate to SignInScreen
            },
          ),
          GestureDetector(
            onTap: () {
              Navigator.pushNamed(
                  context, '/sign-in'); // Navigate to SignInScreen
            },
            child: const Padding(
              padding: EdgeInsets.only(right: 8.0), // Add left padding
              child: Text(
                'Sign In',
                style: TextStyle(fontSize: 16), // Add text beside the icon
              ),
            ),
          ),
        ],
      ),
    );
  }
}
