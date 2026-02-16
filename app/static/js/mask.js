// static/js/mask.js
document.addEventListener('DOMContentLoaded', function() {
  
  // CPF: XXX.XXX.XXX-XX
  const cpfInputs = document.querySelectorAll('input[name="cpf"]');
  cpfInputs.forEach(input => {
    IMask(input, {
      mask: '000.000.000-00'
    });
  });
  
  // TELEFONE: (XX) XXXXX-XXXX (opcional, se precisar)
  const phoneInputs = document.querySelectorAll('input[name="phone"]');
  phoneInputs.forEach(input => {
    IMask(input, {
      mask: '(00) 0 0000-0000'
    });
  });
  
  // Adicione mais máscaras conforme precisar
  // CNPJ: XX.XXX.XXX/XXXX-XX
  const cnpjInputs = document.querySelectorAll('input[name="cnpj"]');
  cnpjInputs.forEach(input => {
    IMask(input, {
      mask: '00.000.000/0000-00'
    });
  });
  
});
