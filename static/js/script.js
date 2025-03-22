document.getElementById("registration-form").addEventListener("submit", function(event) {
    // Name validation
    var name = document.getElementById("name").value;
    if (name.length < 6 || !/^[A-Za-z]+$/.test(name)) {
      alert("Name must be at least 6 characters long and contain only alphabets.");
      event.preventDefault();
    }
  
    // Password validation
    var password = document.getElementById("password").value;
    if (password.length < 6) {
      alert("Password must be at least 6 characters long.");
      event.preventDefault();
    }
  
    // Email validation
    var email = document.getElementById("email").value;
    var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    if (!emailPattern.test(email)) {
      alert("Please enter a valid email address.");
      event.preventDefault();
    }
  
    // Phone validation
    var phone = document.getElementById("phone").value;
    if (phone.length !== 10 || isNaN(phone)) {
      alert("Phone number must be 10 digits long.");
      event.preventDefault();
    }
  });
  