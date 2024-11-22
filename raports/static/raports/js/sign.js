var CADESCOM_CADES_BES = 1;
var CADESCOM_CADES_X_LONG_TYPE_1 = 0x5d;
var CAPICOM_CURRENT_USER_STORE = 2;
var CAPICOM_MY_STORE = "My";
var CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED = 2;
var CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME = 1;


const getCerts = async () => {
// Получает список сертификатов и загружает его в certList
  const $certs = document.getElementById('certList');
  $certs.options.length = 0;
  const $errorMsg = document.getElementById('errorMessage');

  try {
    const certificateList = await window.cryptoPro.getUserCertificates();
    if (certificateList.length == 0) {
        document.getElementById('createSign').disabled = true;
    }
    else {
        document.getElementById('createSign').disabled = false;
    }
    certificateList.forEach(({ name, thumbprint, validTo }) => {
      const $certOption = document.createElement('option');

      $certOption.textContent = `${name} (действителен до: ${new Date(validTo).toLocaleString()})`;
      $certOption.value = thumbprint;

      $certs.appendChild($certOption);
    });
  } catch (e) {
    $errorMsg.textContent = `\n${e.message}`;
  }
};



function Verify(sSignedMessage) {
    // Проверка подписи
    return new Promise(function (resolve, reject) {
        cadesplugin.async_spawn(function* (args) {
            var oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");
            try {
                yield oSignedData.VerifyCades(sSignedMessage, cadesplugin.CADESCOM_CADES_X_LONG_TYPE_1);
            }
            catch (e) {
                err = cadesplugin.getLastError(e);
                alert("Failed to verify signature. Error: " + err);
                return args[1](err);
            }
            return args[0]();
        }, resolve, reject);
    });
}

const sign = async () => {
  document.getElementById('createSign').addEventListener('click', async () => {
      form = document.getElementById('createRaportForm');
      data = document.getElementById('id_text').value;
      const thumbprint = document.getElementById('certList').value;
      value = await window.cryptoPro.createSignature(thumbprint, btoa(unescape(encodeURIComponent(data))));
      document.getElementById('id_sign').value = value;
      form.submit();
          })
};


const waiter = async () => {
    // запускает функции работы с сертификатами при нажатии на кнопку "Сохранить"
    document.getElementById('saveBtn').addEventListener('click', async () => {
      await getCerts();
      await sign();
    })
};

(async () => {
    await waiter();
})();

function SignCreate(certSubjectName, dataToSign) {
    // функция подписания данных, возвращает подпись. Хз как работает
    return new Promise(function (resolve, reject) {
        cadesplugin.async_spawn(function* (args) {
            var oStore = yield cadesplugin.CreateObjectAsync("CAdESCOM.Store");
            yield oStore.Open(CAPICOM_CURRENT_USER_STORE, CAPICOM_MY_STORE,
                CAPICOM_STORE_OPEN_MAXIMUM_ALLOWED);

            var oStoreCerts = yield oStore.Certificates;
            var oCertificates = yield oStoreCerts.Find(
                CAPICOM_CERTIFICATE_FIND_SUBJECT_NAME, certSubjectName);
            var certsCount = yield oCertificates.Count;
            if (certsCount === 0) {
                err = "Certificate not found: " + certSubjectName;
                alert(err);
                args[1](err);
            }
            var oCertificate = yield oCertificates.Item(1);
            var oSigner = yield cadesplugin.CreateObjectAsync("CAdESCOM.CPSigner");
            yield oSigner.propset_Certificate(oCertificate);
            yield oSigner.propset_CheckCertificate(true);
            yield oSigner.propset_TSAAddress("http://cryptopro.ru/tsp/");

            var oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");
            yield oSignedData.propset_Content(dataToSign);

            try {
                var sSignedMessage = yield oSignedData.SignCades(oSigner, CADESCOM_CADES_BES, false);
            }
            catch (e) {
                err = cadesplugin.getLastError(e);
                alert("Failed to create signature. Error: " + err);
                args[1](err);
            }
            yield oStore.Close();
            return args[0](sSignedMessage);
        }, resolve, reject);
    });
}
