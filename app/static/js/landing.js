const formRegister = document.getElementById('form-register');
const nameInput = document.getElementById('name-input');
const phoneNumberInput = document.getElementById('phonenumber-input');
const emailInput = document.getElementById('email-input');
const companyInput = document.getElementById('company-input');


// Check if phone number is valid
function checkPhoneNumber(input){
  // Accept only numbers
  const re = /^[0-9]+$/;
  // Remove caracters
  sanitizePhoneNumber = input.value.replace(/\D/g,'')
  // Test regex
  if(!re.test(sanitizePhoneNumber)){
    return showErrorMessage(input, 'Número de Telefone Inválido.');
  }else if (sanitizePhoneNumber.length <= 9 || sanitizePhoneNumber.length >= 12){
    return showErrorMessage(input, 'Número de Telefone Inválido.');
  }else{
    return hideErrorMessage(input);
  };
};

// Check if email address is valid
function checkEmail(input){
  const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  if(!re.test(input.value.toUpperCase().trim())){
    return showErrorMessage(input, 'E-mail inválido.');
  }else{
    return hideErrorMessage(input);
  }
}

// Show Error Messages
function showErrorMessage(input, errorMessage){
  const formControl = input.parentElement;
  const invalidFeedback = formControl.querySelector('small');
  input.classList.add('is-invalid');
  invalidFeedback.innerText = errorMessage;
  return false;
}

// Hide Messages
function hideErrorMessage(input){
  const formControl = input.parentElement;
  const invalidFeedback = formControl.querySelector('small');
  input.classList.remove('is-invalid');
  invalidFeedback.innerText = '';
  return true;
}

// Check required input is not empty
function checkRequiredInput(input, message){
  if(input.value.trim() === ''){
    return showErrorMessage(input, message)
  }else{
    return hideErrorMessage(input);
  }
}

// Event Listerners
formRegister.addEventListener('submit', (e) =>{
  let validation = true;
  
  // Required Fields
  const requiredFields = [
    {name: nameInput, message: 'Informe o seu Nome Completo.'},
    {name: phoneNumberInput, message: 'Informe o seu número de Telefone.'},
    {name: emailInput, message: 'Informe o seu endereço de E-mail.'},
    {name: companyInput, message: 'Informe o nome da sua Empresa.'}
  ]
  requiredFields.forEach((input) =>{
    validation = checkRequiredInput(input.name, input.message);
  });

  // E-mail validation 
  if (validation){
    validation = checkEmail(emailInput);
  }

  // Phone Number validation
  if (validation){
    validation = checkPhoneNumber(phoneNumberInput);
  }
  // If is invalid not submit
  if (!validation){
    e.preventDefault();
    e.stopPropagation();
  }
});
