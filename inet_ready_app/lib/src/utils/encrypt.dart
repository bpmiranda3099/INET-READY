import 'package:encrypt/encrypt.dart';
import '../utils/xml.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

final key = Key.fromUtf8(dotenv.env['AES_KEY'] ?? 'default_aes_key');
final iv = IV.fromUtf8(dotenv.env['AES_IV'] ?? 'default_aes_iv');
final encrypter = Encrypter(AES(key, mode: AESMode.cbc));

String encryptData(String data) {
  final encrypted = encrypter.encrypt(data, iv: iv);
  return encrypted.base64;
}

String encryptedXmlData = encryptData(xmlData);
