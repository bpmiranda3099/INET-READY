import 'package:http/http.dart' as http;
import 'package:logging/logging.dart';
import '../utils/encrypt.dart';
import '../utils/xml.dart';

Future<void> sendData(String encryptedData) async {
  final response = await http.post(
    Uri.parse('https://your-api-endpoint.com/data'),
    headers: {
      'Content-Type': 'application/xml',
    },
    body: encryptedData,
  );

  if (response.statusCode == 200) {
    Logger('sendData').info('Data sent successfully');
  } else {
    Logger('sendData').severe('Failed to send data');
  }
}

void main() {
  String encryptedXmlData = encryptData(xmlData);
  sendData(encryptedXmlData);
}
