const sidebarItems = document.querySelectorAll(".sidebar-item");
const iframe = document.getElementById("contentFrame");
const hamburgerMenu = document.querySelector(".hamburger-menu");
const sidebar = document.querySelector(".sidebar");
const sidebarOverlay = document.querySelector(".sidebar-overlay");

// Function to check if viewport is mobile
function isMobileView() {
  return window.innerWidth <= 768;
}

// Function to open mobile menu
function openMobileMenu() {
  hamburgerMenu.classList.add("active");
  sidebar.classList.add("mobile-open");
  sidebar.appendChild(hamburgerMenu); // Move hamburger to sidebar when open
  sidebarOverlay.classList.add("active");
  document.body.classList.add("menu-open");
  document.body.style.overflow = "hidden";
}

// Function to close mobile menu
function closeMobileMenu() {
  hamburgerMenu.classList.remove("active");
  sidebar.classList.remove("mobile-open");
  if (hamburgerMenu.parentNode === sidebar) {
    document.querySelector(".teachers-navbar").insertBefore(hamburgerMenu, document.querySelector(".teachers-navbar").firstChild);
  }
  sidebarOverlay.classList.remove("active");
  document.body.classList.remove("menu-open");
  document.body.style.overflow = "auto";
}

// Hamburger menu toggle functionality
if (hamburgerMenu) {
  hamburgerMenu.addEventListener("click", function() {
    if (sidebar.classList.contains("mobile-open")) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });
}

// Close sidebar when overlay is clicked
if (sidebarOverlay) {
  sidebarOverlay.addEventListener("click", closeMobileMenu);
}

// Close sidebar on window resize if in tablet/desktop view
window.addEventListener("resize", function() {
  if (window.innerWidth > 768 && sidebar.classList.contains("mobile-open")) {
    closeMobileMenu();
  }
});

// Handle sidebar item clicks
sidebarItems.forEach(item => {
  item.addEventListener("click", function() {
    // Remove active class from all sidebar items
    sidebarItems.forEach(i => i.classList.remove('active'));
    // Add active class to the clicked sidebar item
    item.classList.add('active');

    // Set iframe source
    const page = item.getAttribute('data-page');
    iframe.src = page;

    // Hide all dropdowns except the clicked one
    sidebarItems.forEach(i => {
      if (i !== item) {
        const dropdownContent = i.querySelector(".dropdown-content");
        const iconArrow = i.querySelector(".icon-arrow");
        if (dropdownContent) dropdownContent.style.display = "none";
        if (iconArrow) {
          iconArrow.classList.remove("up-arrow");
          iconArrow.classList.add("down-arrow");
        }
      }
    });

    // Toggle sidebar and navbar for support-panel
    if (item.id === "support-panel") {
      document.querySelector(".container").classList.add("container-shrink");
      document.querySelector(".teachers-navbar").classList.add("hidden");
      document.querySelector(".sidebar").classList.add("shrink");
    } else {
      document.querySelector(".container").classList.remove("container-shrink");
      document.querySelector(".teachers-navbar").classList.remove("hidden");
      document.querySelector(".sidebar").classList.remove("shrink");
    }
    
    // Close mobile menu after item click if in mobile view
    if (isMobileView()) {
      closeMobileMenu();
    }
  });
});

// Handle dropdown functionality with improved mobile handling
const dropdowns = document.querySelectorAll(".dropdown");
dropdowns.forEach(dropdown => {
  dropdown.addEventListener("click", function(event) {
    event.stopPropagation(); // Prevent the click event from bubbling up
    
    const dropdownContent = this.querySelector(".dropdown-content");
    const iconArrow = this.querySelector(".icon-arrow");
    
    // Toggle dropdown
    if (dropdownContent.style.display === "block") {
      dropdownContent.style.display = "none";
      if (iconArrow) {
        iconArrow.classList.remove("up-arrow");
        iconArrow.classList.add("down-arrow");
      }
    } else {
      dropdownContent.style.display = "block";
      if (iconArrow) {
        iconArrow.classList.remove("down-arrow");
        iconArrow.classList.add("up-arrow");
      }
    }
    
    this.classList.toggle("open");
  });
});

// Handle dropdown item clicks with improved mobile handling
const dropdownItems = document.querySelectorAll(".dropdown-content li");
dropdownItems.forEach(dropdownItem => {
  dropdownItem.addEventListener("click", function(event) {
    event.stopPropagation();
    
    const page = this.getAttribute("data-page");
    iframe.src = page;

    // Remove active class from all sidebar items except the parent
    sidebarItems.forEach(i => {
      if (!i.contains(this)) {
        i.classList.remove("active");
        const dropdownContent = i.querySelector(".dropdown-content");
        const iconArrow = i.querySelector(".icon-arrow");
        if (dropdownContent) dropdownContent.style.display = "none";
        if (iconArrow) {
          iconArrow.classList.remove("up-arrow");
          iconArrow.classList.add("down-arrow");
        }
      }
    });

    // Add active class to parent list item
    const parentItem = this.closest(".sidebar-item");
    parentItem.classList.add("active");
    
    // Close mobile menu after dropdown item click if in mobile view
    if (isMobileView()) {
      closeMobileMenu();
    }
  });
});

// Initialize UI based on screen size
window.addEventListener('DOMContentLoaded', function() {
  if (isMobileView()) {
    // Ensure hamburger is visible on mobile
    if (hamburgerMenu) hamburgerMenu.style.display = 'flex';
  }
});

