function validateCreateAdminUser(errors){
  if (errors.length > 0){
    errors.forEach(error => {
      let input = document.getElementById(`${error.id}`);
      input.classList.add('is-invalid');
      input.nextElementSibling.innerHTML = `${error.message}`;
    });
  }
}