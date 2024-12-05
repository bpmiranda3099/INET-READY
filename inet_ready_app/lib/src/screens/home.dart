import 'package:flutter/material.dart';
import 'package:convex_bottom_bar/convex_bottom_bar.dart';
import 'package:flutter/cupertino.dart';
import 'package:inet_ready_app/src/routes/weather_service.dart';
import 'package:inet_ready_app/src/routes/advisory_service.dart';
import 'package:intl/intl.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  final List<Widget> _screens = [
    DashboardScreen(),
    InetReadyScreen(),
    NotificationsScreen(),
  ];

  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize: Size.fromHeight(70),
        child: ClipRRect(
          borderRadius: BorderRadius.vertical(
            bottom: Radius.circular(15),
          ),
          child: AppBar(
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start, // Align to the left
              children: [
                Text(
                  'INET-READY',
                  style: TextStyle(
                    fontSize: 25,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    shadows: [
                      Shadow(
                        blurRadius: 10.0,
                        color: Colors.black.withOpacity(0.8),
                        offset: Offset(2.0, 2.0),
                      ),
                    ],
                  ),
                ),
                Text(
                  'Your Heat Check for Safe and Informed Travel',
                  style: TextStyle(
                    fontSize: 17,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
            flexibleSpace: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.orange.shade600, Colors.blue.shade400],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
            ),
          ),
        ),
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Color(0xFFFFA726), Color(0xFF42A5F5)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Padding(
                padding: EdgeInsets.only(
                    top: 40.0, left: 16.0, right: 16.0, bottom: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 8),
                    Text(
                      'Rico', // Replace with dynamic user name
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 30,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    Text(
                      'ricob@example.com', // Replace with dynamic email address
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            ListTile(
              leading: Icon(CupertinoIcons.person, size: 30),
              title: const Text(
                'Profile',
                style: TextStyle(
                    fontSize: 22,
                    fontWeight:
                        FontWeight.w500), // Stylish font size and weight
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            Divider(), // Separator for clean look

            // Settings Section (with Icon)
            ListTile(
              leading: Icon(CupertinoIcons.settings, size: 30),
              title: const Text(
                'Settings',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            Divider(),

            // Help & Support Section (with Icon)
            ListTile(
              leading: Icon(CupertinoIcons.question_circle, size: 30),
              title: const Text(
                'Help & Support',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            Divider(),

            // About Section (with Icon)
            ListTile(
              leading: Icon(CupertinoIcons.info, size: 30),
              title: const Text(
                'About',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            Divider(),

            // Feedback Section (with Icon)
            ListTile(
              leading: Icon(CupertinoIcons.chat_bubble, size: 30),
              title: const Text(
                'Feedback',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
            Divider(),

            // Terms & Privacy Section (with Icon)
            ListTile(
              leading: Icon(CupertinoIcons.lock, size: 30),
              title: const Text(
                'Terms & Privacy',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              onTap: () {
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: ConvexAppBar(
        items: [
          TabItem(icon: CupertinoIcons.home, title: 'Dashboard'),
          TabItem(icon: CupertinoIcons.sun_max, title: 'Assess'),
          TabItem(icon: CupertinoIcons.bell, title: 'Notifications'),
        ],
        initialActiveIndex: _selectedIndex,
        onTap: _onItemTapped,
        backgroundColor: Colors.orange.shade400,
        gradient: LinearGradient(
          colors: [Colors.orange.shade600, Colors.blue.shade400],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

String globalCity = '';
String user_id = 'user01';

class _DashboardScreenState extends State<DashboardScreen> {
  String? _selectedCity;
  List<String> _cities = [];
  Map<String, dynamic>? _currentWeather;
  List<Map<String, dynamic>> _forecast = [];
  bool _forecastVisible = false;

  @override
  void initState() {
    super.initState();
    _fetchCities();
  }

  Future<void> _fetchCities() async {
    try {
      final cities = await WeatherService.fetchCities();
      setState(() {
        _cities = cities;
      });
    } catch (e) {
      // Handle error
      print('Error fetching cities: $e');
    }
  }

  Future<void> _fetchWeatherData(String city) async {
    try {
      final currentWeather = await WeatherService.fetchCurrentWeather(city);
      final forecast = await WeatherService.fetchForecast(city);
      setState(() {
        _currentWeather = currentWeather;
        _forecast = forecast;
      });
    } catch (e) {
      // Handle error
      print('Error fetching weather data: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.only(
                top: 16.0, bottom: 0.0, left: 16.0, right: 16.0),
            child: Center(
              child: SizedBox(
                width: 400, // Width of the dropdown button itself
                child: DropdownButtonFormField<String>(
                  decoration: InputDecoration(
                    contentPadding: EdgeInsets.symmetric(horizontal: 16.0),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(15.0),
                      borderSide: BorderSide(color: Colors.white),
                    ),
                    suffixIcon: Icon(CupertinoIcons.location),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                  hint: Text(
                    'Select a city',
                    style: TextStyle(
                      color: Colors.black,
                      shadows: [
                        Shadow(
                          blurRadius: 10.0,
                          color: Colors.black.withOpacity(0.4),
                          offset: Offset(2.0, 2.0),
                        ),
                      ],
                    ),
                  ),
                  value: _selectedCity,
                  onChanged: (String? newValue) {
                    if (newValue != null) {
                      setState(() {
                        _selectedCity = newValue;
                        _fetchWeatherData(newValue);
                      });
                    }
                  },
                  items: _cities.map<DropdownMenuItem<String>>((String city) {
                    return DropdownMenuItem<String>(
                      value: city,
                      child: SizedBox(
                        width: 200, // Adjusted width of dropdown items
                        child: Text(
                          city == 'Dasmariï¿½As' ? 'Dasmariñas' : city,
                          overflow:
                              TextOverflow.ellipsis, // Prevents text overflow
                          style: TextStyle(
                            shadows: [
                              Shadow(
                                blurRadius: 10.0,
                                color: Colors.black.withOpacity(0.5),
                                offset: Offset(2.0, 2.0),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                  icon: SizedBox.shrink(), // Hide the dropdown arrow
                  menuMaxHeight: 600,
                  // Limits dropdown height
                ),
              ),
            ),
          ),
          if (_currentWeather != null) ...[
            Container(
              width: double.infinity, // Make the container take full width
              margin: const EdgeInsets.all(16.0),
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.orange.shade300, Colors.blue.shade400],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(15.0),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.5),
                    spreadRadius: 2,
                    blurRadius: 5,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10.0),
                    child: Text(
                      '${DateFormat.EEEE().format(DateTime.now())}, ${DateTime.now().day} ${DateFormat.MMMM().format(DateTime.now())} ${DateTime.now().year}',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Row(
                    children: [
                      SizedBox(width: 10),
                      Text(
                        double.tryParse(_currentWeather!['heat_index']
                                    .toString()) !=
                                null
                            ? double.parse(_currentWeather!['heat_index']
                                        .toString()) <=
                                    25
                                ? '🌥️ ${_currentWeather!['heat_index']}°C' // Mild weather
                                : double.parse(_currentWeather!['heat_index']
                                            .toString()) <=
                                        32
                                    ? '🌤️ ${_currentWeather!['heat_index']}°C' // Moderate weather
                                    : double.parse(
                                                _currentWeather!['heat_index']
                                                    .toString()) <=
                                            40
                                        ? '☀️ ${_currentWeather!['heat_index']}°C' // High heat
                                        : '🔥 ${_currentWeather!['heat_index']}°C' // Extreme heat
                            : 'Invalid heat index',
                        style: TextStyle(
                          fontSize: 40,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              blurRadius: 10.0,
                              color: Colors.black.withOpacity(0.5),
                              offset: Offset(2.0, 2.0),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        ' HI',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              blurRadius: 10.0,
                              color: Colors.black.withOpacity(0.5),
                              offset: Offset(2.0, 2.0),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const SizedBox(height: 1),
                          Row(
                            children: [
                              const SizedBox(width: 10),
                              Text(
                                ' 🌡️ Temperature: ${_currentWeather!['temperature']}°C',
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                  shadows: [
                                    Shadow(
                                      blurRadius: 10.0,
                                      color: Colors.black.withOpacity(0.5),
                                      offset: const Offset(2.0, 2.0),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            children: [
                              SizedBox(width: 10),
                              Text(
                                ' 💧 Humidity: ${_currentWeather!['humidity']}%',
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                  shadows: [
                                    Shadow(
                                      blurRadius: 15.0,
                                      color: Colors.black.withOpacity(0.5),
                                      offset: Offset(2.0, 2.0),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ],
                      )
                    ],
                  ),
                ],
              ),
            ),
            GestureDetector(
              onTap: () {
                setState(() {
                  // Toggle the visibility of the forecast container
                  _forecastVisible = !_forecastVisible;
                });
              },
              child: Text(
                _forecastVisible
                    ? 'tap to hide forecast ▼'
                    : 'tap to view forecast ▲',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey,
                ),
              ),
            ),
            if (_forecastVisible && _forecast.isNotEmpty) ...[
              Container(
                margin: const EdgeInsets.all(16.0),
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.orange.shade300, Colors.blue.shade400],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(15.0),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.5),
                      spreadRadius: 2,
                      blurRadius: 5,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(height: 0),
                    Text(
                      '7-Day Forecast:',
                      style: TextStyle(
                        fontSize: 24, // Increased font size
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                    ),
                    SizedBox(height: 10), // Add spacing below the title
                    for (var day in _forecast)
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            vertical: 5.0), // Add spacing between days
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                SizedBox(width: 10),
                                Text(
                                  day['condition'] == 'mild'
                                      ? '🌥️  ${day['day']}:'
                                      : day['condition'] == 'moderate'
                                          ? '🌤️  ${day['day']}:'
                                          : day['condition'] == 'high'
                                              ? '☀️  ${day['day']}:'
                                              : '🔥  ${day['day']}:', // Default to extreme heat emoji
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.white,
                                    shadows: [
                                      Shadow(
                                        blurRadius: 10.0,
                                        color: Colors.black.withOpacity(0.5),
                                        offset: Offset(2.0, 2.0),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            Text(
                              '${day['heat_index']}°C',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.w600,
                                color: Colors.white,
                                shadows: [
                                  Shadow(
                                    blurRadius: 10.0,
                                    color: Colors.black.withOpacity(0.5),
                                    offset: Offset(2.0, 2.0),
                                  ),
                                ],
                              ),
                            ),
                            SizedBox(width: 10),
                            Container(
                              width: 150,
                              height: 20,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  colors: day['condition'] == 'mild'
                                      ? [
                                          Colors.green.shade200,
                                          Colors.green.shade500
                                        ]
                                      : day['condition'] == 'moderate'
                                          ? [
                                              Colors.yellow.shade100,
                                              Colors.yellow.shade800
                                            ]
                                          : day['condition'] == 'high'
                                              ? [
                                                  Colors.orange.shade300,
                                                  Colors.orange.shade500
                                                ]
                                              : [
                                                  Colors.red.shade300,
                                                  Colors.red.shade500
                                                ],
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                                borderRadius: BorderRadius.circular(5),
                              ),
                              child: FractionallySizedBox(
                                alignment: Alignment.centerLeft,
                                widthFactor: day['condition'] == 'mild'
                                    ? 0.25
                                    : day['condition'] == 'moderate'
                                        ? 0.5
                                        : day['condition'] == 'high'
                                            ? 0.75
                                            : 1.0,
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.5),
                                    borderRadius: BorderRadius.circular(5),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ],
        ],
      ),
    );
  }
}

class InetReadyScreen extends StatefulWidget {
  const InetReadyScreen({Key? key}) : super(key: key);

  @override
  _InetReadyScreenState createState() => _InetReadyScreenState();
}

class _InetReadyScreenState extends State<InetReadyScreen> {
  double _slidePosition = 0.0;
  bool _isSlidingCompleted = false;
  String _healthAdvisory = '';

  String inetReady = '';
  String importantNotice = '';
  String currentConditions = '';
  String healthRiskAssessment = '';
  String personalizedAdvice = '';
  String generalPrecautions = '';

  // You can replace these with real data or pass as arguments
  String globalCity = 'Dasmariï¿½As';
  String user_id = '11111111-1111-1111-1111-111111111111';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          SizedBox(height: 27),
          // Hide this container after the slide is completed
          if (!_isSlidingCompleted)
            Container(
              width: double.infinity,
              margin: const EdgeInsets.all(16.0),
              padding: const EdgeInsets.all(16.0),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.orange.shade400, Colors.blue.shade400],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(15.0),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.8),
                    spreadRadius: 2,
                    blurRadius: 5,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(bottom: 0),
                    child: Text(
                      'Welcome to the',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 0),
                    child: Text(
                      'INET-READY',
                      style: TextStyle(
                        fontSize: 40,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 0),
                    child: Text(
                      'Health Advisory System',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 0),
                    child: Text(
                      '\nWe are dedicated to providing you with personalized health advice based on your health records. Your information will be used exclusively for this purpose, ensuring that the guidance you receive is tailored to your needs.\n\nPlease be assured that all personal data is handled in full compliance with the Data Privacy Act of 2012 for users within the Philippines, and in accordance with applicable data protection regulations for users outside the country.\n\nOur commitment is to offer accurate, reliable, and actionable advice to support your health and safety.',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black.withOpacity(0.5),
                            offset: Offset(2.0, 2.0),
                          ),
                        ],
                      ),
                      textAlign: TextAlign.justify, // Justify the text
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 0),
                    child: Align(
                      alignment:
                          Alignment.centerRight, // Aligns text to the right
                      child: Text(
                        '\nThe INET-READY Team',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              blurRadius: 10.0,
                              color: Colors.black.withOpacity(0.5),
                              offset: Offset(2.0, 2.0),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  // Add the slider inside the welcome container
                  if (!_isSlidingCompleted)
                    GestureDetector(
                      onHorizontalDragUpdate: (details) {
                        setState(() {
                          _slidePosition += details.primaryDelta!;
                          if (_slidePosition < 0) _slidePosition = 0;
                          if (_slidePosition > 268) _slidePosition = 268;
                        });
                      },
                      onHorizontalDragEnd: (details) async {
                        if (_slidePosition > 134) {
                          setState(() {
                            _slidePosition = 268;
                            _isSlidingCompleted =
                                true; // Hide the slider after completion
                          });
                          // Fetch advisory data
                          try {
                            Map<String, dynamic> advisory =
                                await AdvisoryService.fetchHealthAdvisory(
                                    globalCity, user_id);
                            setState(() {
                              _healthAdvisory = advisory['advisory'] ??
                                  'No advisory available.';
                              splitAdvisory(_healthAdvisory);
                            });
                          } catch (e) {
                            setState(() {
                              _healthAdvisory =
                                  'Failed to load health advisory.';
                            });
                          }
                        } else {
                          setState(() {
                            _slidePosition = 0;
                          });
                        }
                      },
                      child: Container(
                        width: double.infinity,
                        height: 60,
                        margin: const EdgeInsets.only(top: 20),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Colors.orange.shade200,
                              Colors.blue.shade400
                            ],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(15.0),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.3),
                              spreadRadius: -5,
                              blurRadius: 8,
                              offset: Offset(0, 5),
                            ),
                          ],
                        ),
                        child: Stack(
                          alignment: Alignment.center,
                          children: [
                            Text(
                              'INET-READY?',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 30,
                                shadows: [
                                  Shadow(
                                    blurRadius: 10.0,
                                    color: Colors.black.withOpacity(0.5),
                                    offset: Offset(2.0, 2.0),
                                  ),
                                ],
                              ),
                            ),
                            Positioned(
                              left: _slidePosition,
                              child: Container(
                                width: 60,
                                height: 60,
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.5),
                                  borderRadius: BorderRadius.circular(15.0),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Color.fromARGB(255, 209, 208, 208)
                                          .withOpacity(0.4),
                                      spreadRadius: 2,
                                      blurRadius: 5,
                                      offset: Offset(0, 2),
                                    ),
                                  ],
                                ),
                                child: Center(
                                  child: Text(
                                    _slidePosition > 134 ? '💪' : '🔥',
                                    style: TextStyle(
                                      fontSize: 30,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  Padding(
                    padding: const EdgeInsets.only(top: 15.0),
                    child: Center(
                      child: Text(
                        'slide to continue >>',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              blurRadius: 10.0,
                              color: Colors.black.withOpacity(0.5),
                              offset: Offset(2.0, 2.0),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          // Display the fetched advisory when sliding is completed
          if (_isSlidingCompleted)
            Expanded(
                child: ListView(
              children: [
                if (importantNotice.isNotEmpty)
                  _buildImportantNoticeSection(
                      "⚠️  IMPORTANT NOTICE", importantNotice),
                if (inetReady.isNotEmpty)
                  _buildInetReadySection("YOU ARE", inetReady),
                if (currentConditions.isNotEmpty)
                  _buildCurrentConditionsSection(
                      "⛅  CURRENT CONDITIONS", currentConditions),
                if (healthRiskAssessment.isNotEmpty)
                  _buildHealthRiskAssessmentSection(
                      "❤️  HEALTH RISK ASSESSMENT", healthRiskAssessment),
                if (personalizedAdvice.isNotEmpty)
                  _buildPersonalizedAdviceSection(
                      "🤝  PERSONALIZED ADVICE", personalizedAdvice),
                if (generalPrecautions.isNotEmpty)
                  _buildAdvisorySection(
                      "🫡  GENERAL PRECAUTIONS", generalPrecautions),
              ],
            )),
        ],
      ),
    );
  }

  Widget _buildInetReadySection(String title, String content) {
    // Check if content contains the word "NOT"
    bool containsNot = content.toUpperCase().contains("NOT");

    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        // Change gradient based on the content
        gradient: LinearGradient(
          colors: containsNot
              ? [Colors.red.shade700, Colors.red.shade300] // Gradient of red
              : [
                  Colors.green.shade700,
                  Colors.green.shade300
                ], // Gradient of green
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.8),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 0),
          Center(
            child: Text(
              content,
              style: TextStyle(
                fontSize: 55,
                fontWeight: FontWeight.w400,
                color: Colors.white,
                shadows: [
                  Shadow(
                    blurRadius: 10.0,
                    color: Colors.black.withOpacity(0.5),
                    offset: Offset(2.0, 2.0),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImportantNoticeSection(String title, String content) {
    return GestureDetector(
      onTap: () {
        setState(() {
          importantNotice = '';
        });
      },
      child: Container(
        padding: const EdgeInsets.all(16.0),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.orange.shade500, Colors.red.shade500],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(15.0),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.8),
              spreadRadius: 2,
              blurRadius: 5,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 25,
                fontWeight: FontWeight.w600,
                color: Colors.white,
                shadows: [
                  Shadow(
                    blurRadius: 10.0,
                    color: Colors.black.withOpacity(0.5),
                    offset: Offset(2.0, 2.0),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 5),
            Text(
              'This advice aligns with the international health guidelines, and your health data is processed in compliance with the Data Privacy Act of 2012 (Philippines) or applicable regulations in your region.',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w400,
                color: Colors.white,
                shadows: [
                  Shadow(
                    blurRadius: 10.0,
                    color: Colors.black.withOpacity(0.5),
                    offset: Offset(2.0, 2.0),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 15),
            Center(
              child: Text(
                'tap to dismiss',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentConditionsSection(String title, String content) {
    // Extract and parse the numeric value from the content
    double value =
        double.tryParse(RegExp(r'\d+(\.\d+)?').stringMatch(content) ?? '0') ??
            0;

    // Determine the gradient colors based on the numeric value
    List<Color> gradientColors;
    if (value <= 27) {
      gradientColors = [Colors.green.shade500, Colors.green.shade300];
    } else if (value > 27 && value <= 32) {
      gradientColors = [Colors.yellow.shade800, Colors.yellow.shade600];
    } else if (value > 32 && value <= 39) {
      gradientColors = [Colors.orange.shade400, Colors.orange.shade300];
    } else if (value > 39) {
      gradientColors = [Colors.red.shade500, Colors.red.shade400];
    } else {
      gradientColors = [
        Colors.blue.shade200,
        Colors.green.shade400
      ]; // Default colors
    }

    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: gradientColors,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.8),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Text(
            content,
            style: TextStyle(
              fontSize: 21,
              fontWeight: FontWeight.w400,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.9),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthRiskAssessmentSection(String title, String content) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.grey, Colors.black],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.8),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Text(
            content,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w400,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.5),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAdvisorySection(String title, String content) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.purple.shade500, Colors.lightGreen],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.8),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Text(
            content,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w400,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPersonalizedAdviceSection(String title, String content) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade500, Colors.green.shade300],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(15.0),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.8),
            spreadRadius: 2,
            blurRadius: 5,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          Text(
            content,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w400,
              color: Colors.white,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.black.withOpacity(0.8),
                  offset: Offset(2.0, 2.0),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

// Split advisory content into sections
  void splitAdvisory(String advisory) {
    // Use a regular expression to match sections and titles.
    final regex = RegExp(r'([A-Za-z\s]+:)([\s\S]+?)(?=\n[A-Za-z\s]+:|\n*$)',
        dotAll: true);

    // Find all the matches
    final matches = regex.allMatches(advisory);

    List<String> sectionTitles = [];
    List<String> sectionContents = [];

    // Extract the titles and contents correctly
    for (final match in matches) {
      String sectionTitle = match.group(1)?.trim() ?? '';
      String sectionContent = match.group(2)?.trim() ?? '';

      if (sectionTitle.isNotEmpty && sectionContent.isNotEmpty) {
        sectionTitles.add(sectionTitle);
        sectionContents.add(sectionContent);
      }
    }

    // Now map the titles and contents to specific variables
    setState(() {
      inetReady = sectionContents.isNotEmpty ? sectionContents[0] : '';
      importantNotice = sectionContents.isNotEmpty ? sectionContents[1] : '';
      currentConditions = sectionContents.length > 1 ? sectionContents[2] : '';
      healthRiskAssessment =
          sectionContents.length > 3 ? sectionContents[3] : '';

      // Bullet each sentence in personalizedAdvice if content exists
      personalizedAdvice = sectionContents.length > 4
          ? _bulletEachSentence(sectionContents[4])
          : '';

      // Ensure generalPrecautions is assigned correctly
      generalPrecautions = sectionContents.length > 5
          ? sectionContents[5]
          : ''; // Empty string if not found

      // If generalPrecautions is still empty, handle that case
      if (generalPrecautions.isEmpty &&
          advisory.contains('General Precautions:')) {
        final generalPrecautionsRegex = RegExp(
            r'General Precautions:\s*([\s\S]+?)(?=\n[A-Za-z\s]+:|\n*$)',
            dotAll: true);
        final generalPrecautionsMatch =
            generalPrecautionsRegex.firstMatch(advisory);
        generalPrecautions = generalPrecautionsMatch?.group(1)?.trim() ??
            'No general precautions available.';
      }

      // If all sections are empty, set default data
      if (inetReady.isEmpty &&
          importantNotice.isEmpty &&
          currentConditions.isEmpty &&
          healthRiskAssessment.isEmpty &&
          personalizedAdvice.isEmpty &&
          generalPrecautions.isEmpty) {
        inetReady = 'No data available.';
        importantNotice = 'No data available.';
        currentConditions = 'No data available.';
        healthRiskAssessment = 'No data available.';
        personalizedAdvice = 'No data available.';
        generalPrecautions = 'No data available.';
      }
    });
  }

// Function to bullet each sentence
  String _bulletEachSentence(String content) {
    // Split content by sentences (simple approach using periods followed by a space or end of string)
    List<String> sentences = content.split(RegExp(r'(?<=\.)\s+'));

    // Bullet each sentence
    return sentences.map((sentence) => '📝  $sentence').join('\n');
  }
}

@override
class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({Key? key}) : super(key: key);

  @override
  NotificationsScreenState createState() => NotificationsScreenState();
}

class NotificationsScreenState extends State<NotificationsScreen> {
  bool _isNotificationsEnabled = false;
  List<String> _notifications = [
    "New health advisory available!",
    "Weather update: High heat alert in your area.",
    "Reminder: Check your heat safety settings.",
  ];

  // Toggle notification settings
  void _toggleNotifications(bool value) {
    setState(() {
      _isNotificationsEnabled = value;
    });
  }

  // Simulate adding a new notification with varying content at the top
  void _addNewNotification() {
    final List<String> randomNotifications = [
      "New health advisory available!",
      "Weather update: High heat alert in your area.",
      "Reminder: Check your heat safety settings.",
      "Heat wave expected tomorrow, stay safe!",
      "Temperature has reached unsafe levels, take precautions.",
      "Humidity levels rising, be cautious when outdoors.",
    ];

    final randomIndex =
        (randomNotifications..shuffle()).first; // Shuffle and pick random

    setState(() {
      // Add new notification at the top
      _notifications.insert(0, randomIndex);
    });
  }

  // Function to determine gradient based on notification type
  LinearGradient _getNotificationGradient(String notification) {
    if (notification.contains("health advisory")) {
      return const LinearGradient(
        colors: [Colors.greenAccent, Colors.blue],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else if (notification.contains("heat alert") ||
        notification.contains("heat wave") ||
        notification.contains("unsafe levels")) {
      return const LinearGradient(
        colors: [Colors.redAccent, Colors.orangeAccent],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else if (notification.contains("Reminder")) {
      return const LinearGradient(
        colors: [Colors.blueAccent, Colors.purpleAccent],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else {
      return const LinearGradient(
        colors: [Colors.black, Colors.grey],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Switch(
                  value: _isNotificationsEnabled,
                  onChanged: _toggleNotifications,
                ),
                const Text(
                  '   Enable Notifications',
                  style: TextStyle(
                    fontSize: 20,
                  ),
                ),
                const SizedBox(width: 16), // Space between switch and button
                // Invisible button placed on the right side
                GestureDetector(
                  onTap: _addNewNotification,
                  child: Opacity(
                    opacity: 0, // Invisible button
                    child: ElevatedButton(
                      onPressed: _addNewNotification,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12.0),
                        backgroundColor:
                            Colors.transparent, // Transparent background
                      ),
                      child: const Text(
                        'Simulate New Notification',
                        style: TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'Recent Notifications:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 22),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: _notifications.length,
                itemBuilder: (context, index) {
                  return Container(
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    padding: const EdgeInsets.all(16.0),
                    decoration: BoxDecoration(
                      gradient: _getNotificationGradient(_notifications[index]),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.notifications,
                          color: Colors.white,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _notifications[index],
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18, // Increased font size
                              fontWeight: FontWeight.w600,
                              shadows: [
                                Shadow(
                                  color: Colors.black,
                                  offset: Offset(2, 2),
                                  blurRadius: 3,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            // Settings button (if any)
          ],
        ),
      ),
    );
  }
}
