import 'package:encrypt/encrypt.dart';
import '../utils/xml.dart';

final key = Key.fromUtf8('your-32-byte-key-here');
final iv = IV.fromUtf8('your-16-byte-iv-here');
final encrypter = Encrypter(AES(key, mode: AESMode.cbc));

String encryptData(String data) {
  final encrypted = encrypter.encrypt(data, iv: iv);
  return encrypted.base64;
}

String encryptedXmlData = encryptData(xmlData);
