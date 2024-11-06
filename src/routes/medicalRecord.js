const axios = require('axios');
const crypto = require('crypto');

const key = Buffer.from('your-32-byte-key-here', 'utf8'); 
const iv = Buffer.from('your-16-byte-iv-here', 'utf8');   

function decryptData(encryptedData) {
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encryptedData, 'base64', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

axios.post('https://your-api-endpoint.com/data')
  .then(response => {
    const encryptedData = response.data;
    const decryptedData = decryptData(encryptedData);
    console.log('Decrypted Data:', decryptedData);
  })
  .catch(error => {
    console.error('Error receiving data:', error);
  });