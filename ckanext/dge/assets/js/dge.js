/*
* Copyright (C) 2025 Entidad Pública Empresarial Red.es
*
* This file is part of "dge (datos.gob.es)".
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*/

(function($){
	$(document).ready(function(){

		$('.nav-search-menu').click(function(){
			$('.block-search').toggleClass('open-search-menu');
		});

		$('.toggle-replies').click(function(){
			$(this).toggleClass('toggle-replies-active');
		});

		/*::::::::: CUSTOM SELECT BODY ::::::::*/
		$('.custom_select-body').click(function(e) {
			e.stopPropagation();
			$('.custom_select-body').not(this).removeClass('select-visible');
			$(this).toggleClass('select-visible');
		});

		$('.custom_select ul').click(function(e) {
			e.stopPropagation();
		});

		$('.leaf.has-children').click(function(e) {
            $('.leaf.has-children').not(this).removeClass('is-visible');
            $(this).toggleClass('is-visible');
        });

        $(document).click(function() {
            $('.leaf.has-children').removeClass('is-visible');
        });

		$(document).click(function(e) {
		    if (!$(e.target).closest('.custom_select').length) {
		        $('.custom_select-body').removeClass('select-visible');
		    }
		});

		$(document).ready(function() {
			$('.select2-search-field').prependTo('.select2-choices');
		});

		function initDgeSearchDropdown() {
			const dropdownWrapper = document.querySelector('.dge-search-dropdown-wrapper');
			const trigger = dropdownWrapper.querySelector('.dge-search-dropdown-trigger');
			const menu = dropdownWrapper.querySelector('.dge-search-dropdown-menu');
			const hiddenInput = document.querySelector('#dge-search-hidden-input');
		
			const selectedItem = menu.querySelector('.dge-search-selected');
			if (selectedItem) {
				trigger.textContent = selectedItem.textContent; 
			}
		
			trigger.addEventListener('click', () => {
				dropdownWrapper.classList.toggle('active');
			});
		
			menu.addEventListener('click', (e) => {
				if (e.target.classList.contains('dge-search-dropdown-item')) {
					const value = e.target.getAttribute('data-value');
					const label = e.target.textContent;
		
					hiddenInput.value = value;
					trigger.textContent = label;
		
					menu.querySelectorAll('.dge-search-dropdown-item').forEach(item => item.classList.remove('dge-search-selected'));
					e.target.classList.add('dge-search-selected');
		
					dropdownWrapper.classList.remove('active');
		
					const form = dropdownWrapper.closest('form');
					if (form) {
						form.submit();
					}
				}
			});
		
			document.addEventListener('click', (e) => {
				if (!dropdownWrapper.contains(e.target)) {
					dropdownWrapper.classList.remove('active');
				}
			});
		}
		
		$(document).ready(function () {
			if (document.querySelector('.dge-search-dropdown-wrapper')) {
				initDgeSearchDropdown();
			}
		});

		// Allows checkbox of the side filters of catalogues page to change url (apply filter)
		// Target all checkboxes inside the custom_select component
		$('.custom_select input[type="checkbox"]').on('change', function () {
			// Get the href value from the data-href attribute of the checkbox
			var url = $(this).data('href');
			
			// Redirect to the new URL
			if (url) {
				window.location.href = url;
			}
		});
		


		const dropdownButton = document.querySelector('.custom-btn-search');
		const dropdownMenu = document.querySelector('.search-filter');
		const dropdownItems = document.querySelectorAll('#opciones .dropdown-item');
		const hiddenInput = document.getElementById('search-filter-hidden');
		dropdownButton.addEventListener('click', function() {
		dropdownMenu.classList.toggle('show');
		});

		dropdownItems.forEach(item => {
		item.addEventListener('click', function() {

			const selectedValue = item.getAttribute('data-value');
			hiddenInput.value = selectedValue;
			dropdownButton.textContent = item.textContent;

			dropdownMenu.classList.remove('show');
		});
		});

		document.addEventListener('click', function(event) {
		const isClickInside = dropdownButton.contains(event.target) || dropdownMenu.contains(event.target);
		if (!isClickInside) {
			dropdownMenu.classList.remove('show');
		}
		});




		/*::::::::: FOCUS CONDICIONES :::::::: */
		 $('#edit-mail').focus(function() {
			$('#footer-conditions').show();
		 });

		/*::::::::: LOGIN responsive :::::::: */

		$('.dge-mobileuser').click(function(){
			$('body').addClass('login-modal');
		});
		$('.closeLogin').click(function(){
			$('body').removeClass('login-modal');
		});

		/*::::::::: MENU SCROLL stiky ::::::::*/
		var stikyNav = $('.site-navigation');
		var stikyHeight = $('.site-navigation').offset();
		$(window).scroll(function (){
			if ($(this).scrollTop() > (stikyHeight.top)){
				stikyNav.addClass("stiky");
			} else {
				stikyNav.removeClass("stiky");
			}
		});


		/*::::::::: SEARCH responsive :::::::: */
		$('.block-search form').before('<a class="closeModalMD closeSearch"><i class="icon-remove-sign"></i><span class="element-invisible">close</span></a>');

		$('.dge-mobilesearch').click(function(){
			$('body').addClass('search-modal');
		});
		$('.closeSearch').click(function(){
			$('body').removeClass('search-modal');
		});

		/*::::::::: HEADER Social Networks hover :::::::: */
		$('.region-header .dge-social-links .content a').bind('mouseenter focusin', function(){
			var src = $(this).find('img').attr('src');
			if(src.indexOf('-alt.svg') == -1){
				src = $(this).find('img').attr('src').match(/[^\.]+/) + '-alt.svg';
				$(this).find('img').attr("src", src);
			}
		}).bind('mouseleave focusout', function(){
			var src = $(this).find('img').attr("src").replace("-alt.svg", ".svg");
            $(this).find('img').attr("src", src);
		});

		/*::::::::: MENU MAIN lateral :::::::: */
		$('.dge-mobilemenu').sidr({
			name: 'dge-main-menu--rwd',
			source: '.dge-submenu',
			side: 'right'
		});
		$('#dge-main-menu--rwd').insertAfter('.dge-mobilenav');


		/*::::::::: MENU MAIN desplegable :::::::: */
		var oldSection = $(this).find('.active-trail a').attr('href');
		$('.dge-main-menu a[href^="#"]').click(function(){
			var dgeSection = $(this).attr('href');

			if(oldSection == dgeSection){
				$('.dge-main-menu a').parent('li').removeClass('is-visible');
				$('.block-search').removeClass('is-visible'); //Search menu invisible
				$('.dge-user-menu, .block-user').removeClass('is-visible'); //User menu invisible
				$('.dge-submenu li').removeClass('is-visible').parent('.menu').removeClass('is-visible');
				oldSection = '';
				return false;
			}else{
				$('.dge-main-menu a').parent('li').removeClass('is-visible');
				$(this).parent('li').toggleClass('is-visible');

				if(dgeSection == '#search'){
					$('.dge-submenu').removeClass('is-visible'); //Submenu invisible
					$('.dge-user-menu, .block-user').removeClass('is-visible'); //User menu invisible
					$('.block-search').addClass('is-visible').find('.form-text').focus(); //Search form visible and focus
				} else if(dgeSection == '#login'){
					$('.dge-submenu').removeClass('is-visible'); //Submenu invisible
					$('.block-search').removeClass('is-visible'); //Search menu invisible
					$('.dge-user-menu, .block-user').addClass('is-visible').find('.form-item-name .form-text').focus(); //User form o menu visible and focus
				} else {
					$('.block-search').removeClass('is-visible'); //Search menu invisible
					$('.dge-user-menu, .block-user').removeClass('is-visible'); //User menu invisible
					$('.dge-submenu li').removeClass('is-visible').parent('.menu').removeClass('is-visible');
					$('.dge-submenu').addClass('is-visible'); //Submenu visible
					$('.dge-submenu a[href="' + dgeSection + '"]').parent('li').addClass('is-visible').parent('.menu').addClass('is-visible').find('li:first-child a').focus();
				}
			}

			oldSection = dgeSection;
			return false;
		});
		$('.dge-submenu li.active-trail').addClass('is-visible').parents('.dge-submenu').addClass('is-visible');
		$('.block-user .form-item-pass .form-text').on('blur', function(){
			$('.block-user .form-submit').focus();
		});


		// Filter search functionality in the input of the dropdown filter
		$('.filter-input').on('keyup', function() {
			var value = $(this).val().toLowerCase(); // Get the input value and convert to lowercase
			var filterList = $(this).closest('.custom_select-body').siblings('ul'); // Find the related list
	
			filterList.find('.facet-item').filter(function() {
				// Show items that match the input, hide those that don't
				$(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
			});
		});  

		/*:::: MENU Tootltips ::::*/
		$('.dge-main-menu .block__content a[href="#search"]').attr('data-tooltip', function(){return $(this).text();});
		$('.dge-main-menu .block__content a[href="#login"]').attr('data-tooltip', function(){return $(this).text();});

		/*::::::::: FILTERS active :::::::: */
		$('.pane-facetapi .facetapi-active').parent('li').addClass('is-active');

		/*:::::::: CATEGORY LIST ::::::*/
		if($('.dataset-categories').height() > 100){
			$('.dataset-categories').addClass('dataset-categories-full');
		} else {
			$('.dge-category-list').addClass('dataset-categories-mini');
		};
		//dataset list - more than 3 categories
		if (window.matchMedia("(min-width: 60em)").matches) {
			$('.dge-list--dataset .dataset-categories').each(function(){
				if($(this).children().length > 3){
					$(this).addClass('categories-full');
					$(this).after('<a class="categories-open open"><i class="icon-open-sign"></i><span class="element-invisible">Open</span></a>');
				};
			});
			$('.categories-open').click(function(){
				$(this).toggleClass('is-active');
				$(this).prev('.categories-full').toggleClass('selected');
			});
		};

		/*:::::::: NEWSLETTER GDPR ::::::*/
		var $newsletterForm = $('form#simplenews-block-form-21');
		var $input = $newsletterForm.find('input#edit-mail');
		var $input2 = $newsletterForm.find('input#edit-mail--2');
    	var $terms_field = $newsletterForm.find('.form-type-checkbox');

	  	$terms_field.hide();

		function show_legal() {
				$terms_field.slideDown(700);
		}
		$input.on('focus', function() {
				if ($("#edit-action2-subscribe").prop("checked")) {
					show_legal();
				}
				if ($("#edit-action2-unsubscribe").prop("checked")) {
					$terms_field.slideUp(700);
				}
			});
		$input2.on('focus', function() {
			if ($("#edit-action2-subscribe").prop("checked")) {
					show_legal();
			}
		});
		$('input#edit-submit--4').click(function(){
			if ($("#edit-action2-unsubscribe").prop("checked")) {
				$terms_field.remove();
			}
		});


		function initializeReadMoreSections() {
			const readMoreSections = document.querySelectorAll(".read-more");
	
			readMoreSections.forEach((readMoreContainer) => {
				const readMoreBottom = readMoreContainer.nextElementSibling; 
	
				if (readMoreBottom && readMoreBottom.classList.contains("read-more__bottom")) {
					readMoreContainer.style.transition = "height 0.3s ease-in-out";
	
					let maxHeight = 160; 
					if (readMoreContainer.classList.contains("read-more--md")) {
						maxHeight = 400;
					} else if (readMoreContainer.classList.contains("read-more--lg")) {
						maxHeight = 600;
					}
	
					const offsetAdjustment = 180; 
					let isExpanded = false; 
	
					function updateReadMoreState() {
						if (!isExpanded) { 
							const isVisible = readMoreContainer.offsetParent !== null; 
							if (isVisible && readMoreContainer.scrollHeight > maxHeight) {
								readMoreContainer.style.height = `${maxHeight}px`;
								readMoreBottom.style.display = "flex";
							} else {
								readMoreBottom.style.display = "none";
							}
						}
					}
	
					updateReadMoreState(); 
	
					readMoreBottom.addEventListener("click", function () {
						if (!isExpanded) {
							readMoreContainer.style.height = "auto";
							readMoreContainer.classList.add("expand");
							readMoreBottom.querySelector("button").textContent = readMoreBottom.querySelector("button").getAttribute("data-less");
							isExpanded = true;
						} else {
							readMoreContainer.style.height = `${maxHeight}px`;
							readMoreContainer.classList.remove("expand");
							readMoreBottom.querySelector("button").textContent = readMoreBottom.querySelector("button").getAttribute("data-more");
							isExpanded = false;
	
							const rect = readMoreContainer.getBoundingClientRect();
							const scrollTop = window.scrollY || document.documentElement.scrollTop;
							window.scrollTo({ top: rect.top + scrollTop - offsetAdjustment, behavior: "smooth" });
						}
					});
	
					const resizeObserver = new ResizeObserver(() => {
						setTimeout(updateReadMoreState, 100); 
					});
	
					resizeObserver.observe(readMoreContainer);
				}
			});
		}

		initializeReadMoreSections(); 

		var filterContainer = document.getElementById("filter-container");
		var filterButton = document.getElementById("filter-container__button");
		var closeButton = document.getElementById("close-filter");
		
		filterButton?.addEventListener("click", function(event) {
			event.preventDefault();
			filterContainer.classList.toggle("open");
			toggleScroll();
			scrollToTop(); // Call the function to scroll to the top
		});
		
		closeButton?.addEventListener("click", function(event) {
			event.preventDefault();
			filterContainer.classList.remove("open");
			toggleScroll();
		});
		
		// Listen for window resize
		window.addEventListener("resize", handleResize);
		
		// Function to handle window resize
		function handleResize() {
			if (filterContainer.classList.contains("open")) {
			toggleScroll();
			}
			// Remove "open" class if window width is greater than 768 pixels
			if (window.innerWidth > 768) {
			filterContainer.classList.remove("open");
			document.body.style.overflow = "auto";
			}
		}
		
		// Function to toggle scroll behavior
		function toggleScroll() {
			document.body.style.overflow = filterContainer.classList.contains("open") ? "hidden" : "auto";
		}
		
		// Function to scroll to top
		function scrollToTop() {
			window.scrollTo({
			top: 0,
			behavior: "smooth" // Smooth scrolling behavior
			});
		}
		});

		document.addEventListener("DOMContentLoaded", function() {
		var filterContainer = document.querySelector(".secondary");
		var filterButton = document.querySelector(".button-arrow-filter-mobile");
		var closeButton = document.querySelector(".close-filters");
		
		filterButton?.addEventListener("click", function(event) {
			event.preventDefault();
			filterContainer.classList.add("filter-visible");
			toggleScroll();
			scrollToTop();
		});
		
		closeButton?.addEventListener("click", function(event) {
			event.preventDefault();
			filterContainer.classList.remove("filter-visible");
			toggleScroll();
		});
		
		window.addEventListener("resize", handleResize);
		function handleResize() {
			if (window.innerWidth > 768) {
			filterContainer.classList.remove("filter-visible");
			document.body.style.overflow = "auto";
			}
		}
		function toggleScroll() {
			document.body.style.overflow = filterContainer.classList.contains("filter-visible") ? "hidden" : "auto";
		}
		function scrollToTop() {
			window.scrollTo({
			top: 0,
			behavior: "smooth"
			});
		}

		const targetElement = document.querySelector(".site-page");

		if (!targetElement) {
			console.error("Element with class 'site-page' not found.");
			return;
		}
		
		/* **** */
		/* CodeMirror adapt fullscreen */
		/* **** */
		const observer = new MutationObserver(function (mutationsList) {
			const codeMirror = document.querySelector(".CodeMirror");
			const yasr = document.querySelector(".yasr");
		
			const isFullscreen =
				(codeMirror && codeMirror.classList.contains("CodeMirror-fullscreen")) ||
				(yasr && yasr.classList.contains("yasr_fullscreen"));
		
			targetElement.style.display = isFullscreen ? "none" : "";
			document.body.style.overflow = isFullscreen ? "hidden" : ""; 
		});
		
		observer.observe(document.body, {
			attributes: true,
			subtree: true,
			attributeFilter: ["class"]
		});
		/* **** */
		/* END CodeMirror adapt fullscreen */
		/* **** */

		/* **** */
		/* BURGER NAV MENU FUNTIONALITY */
		/* **** */
		// Always define these at the top
		function openNavMenu() {
			$('.nav-menu-trigger.nav-burger-menu').addClass('open-burger-menu');
			$('body').addClass('block-scroll');
		}
		
		function closeNavMenu() {
			$('.nav-menu-trigger.nav-burger-menu').removeClass('open-burger-menu');
			$('body').removeClass('block-scroll');
		}
		
		function closeOnClickOutside(event) {
			var menu = $('.dge-main-menu');
			var button = $('.nav-menu-trigger.nav-burger-menu');
			var closeButton = $('.close-menu-button');
		
			if (
			(!menu.is(event.target) && menu.has(event.target).length === 0) ||
			closeButton.is(event.target)
			) {
			closeNavMenu();
			}
		}
		
		const burgerTrigger = document.querySelector('.nav-menu-trigger.nav-burger-menu');
		
		if (burgerTrigger) {
			// Ensure it's focusable
			if (!burgerTrigger.hasAttribute('href')) {
			burgerTrigger.setAttribute('tabindex', '0');
			}
		
			// Toggle aria-expanded
			const updateAria = () => {
			const isOpen = burgerTrigger.classList.contains('open-burger-menu');
			burgerTrigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
			};
		
			// Keyboard support
			burgerTrigger.addEventListener('keydown', (e) => {
			const isOpen = burgerTrigger.classList.contains('open-burger-menu');
			if (e.key === 'Enter' || e.key === ' ') {
				e.preventDefault();
				if (!isOpen) {
				openNavMenu();
				} else {
				closeNavMenu();
				}
				updateAria();
			} else if (e.key === 'Escape' && isOpen) {
				closeNavMenu();
				updateAria();
				burgerTrigger.focus();
			}
			});
		
			// Click toggle
			$('.nav-menu-trigger.nav-burger-menu').click(function (event) {
			event.stopPropagation();
			const isOpen = $(this).hasClass('open-burger-menu');
		
			if (!isOpen) {
				openNavMenu();
			} else {
				closeNavMenu();
			}
			updateAria();
			});
		
			// Outside click closes
			$(document).on('click', function (event) {
			closeOnClickOutside(event);
			updateAria();
			});
		}
  
		/* **** */
		/* END - BURGER NAV MENU FUNTIONALITY */
		/* **** */

		/* **** */
		/* Language Switcher */
		/* **** */
		const dropdown = document.querySelector('.language-switcher');
		if (dropdown) {
		  const links = dropdown.querySelectorAll('.links a');
		  const ariaToggle = () => {
			const expanded = dropdown.classList.contains('is-open');
			dropdown.setAttribute('aria-expanded', expanded ? 'true' : 'false');
		  };
		  // Toggle on click
		  dropdown.addEventListener('click', function (event) {
			if (event.target.closest('.links')) {
			  return; // Don't toggle when clicking a link
			}
			dropdown.classList.toggle('is-open');
			ariaToggle();
		  });
		  // Keyboard support on the dropdown container
		  dropdown.addEventListener('keydown', function (e) {
			const isOpen = dropdown.classList.contains('is-open');
			const isInsideLinks = e.target.closest('.links');
			if ((e.key === 'Enter' || e.key === ' ') && !isInsideLinks) {
			  e.preventDefault();
			  dropdown.classList.toggle('is-open');
			  ariaToggle();
			} else if (e.key === 'Escape' && isOpen) {
			  dropdown.classList.remove('is-open');
			  ariaToggle();
			  dropdown.focus();
			}
		  });
		  // Open dropdown when any of the links receive focus
		  links.forEach(link => {
			link.addEventListener('focus', () => {
			  dropdown.classList.add('is-open');
			  ariaToggle();
			});
		  });
		  // Close on outside click
		  document.addEventListener('click', function (event) {
			if (!dropdown.contains(event.target)) {
			  if (dropdown.classList.contains('is-open')) {
				dropdown.classList.remove('is-open');
				ariaToggle();
			  }
			}
		  });
		}
		/* **** */
		/* END Language Switcher */
		/* **** */

		/* **** */
		/* USER LOGIN MENU (NOT LOGGED IN)  */
		/* **** */
		const loginTrigger = document.querySelector('.user-login');
		const loginMenu = document.querySelector('.submenu-children-login');
		if (loginTrigger && loginMenu) {
		const toggleLoginMenu = () => {
			const expanded = loginMenu.classList.toggle('is-visible');
			loginTrigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
		};
		const closeLoginMenu = () => {
			loginMenu.classList.remove('is-visible');
			loginTrigger.setAttribute('aria-expanded', 'false');
		};
		loginTrigger.addEventListener('click', (e) => {
			toggleLoginMenu();
		});
		loginTrigger.addEventListener('keydown', function (e) {
			const isOpen = loginMenu.classList.contains('is-visible');
			if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			toggleLoginMenu();
			} else if (e.key === 'Escape' && isOpen) {
			closeLoginMenu();
			loginTrigger.focus();
			}
		});
		const loginLinks = loginMenu.querySelectorAll('a');
		loginLinks.forEach(link => {
			link.addEventListener('focus', () => {
			loginMenu.classList.add('is-visible');
			loginTrigger.setAttribute('aria-expanded', 'true');
			});
		});
		document.addEventListener('click', function (e) {
			if (!loginMenu.contains(e.target) && !loginTrigger.contains(e.target)) {
			closeLoginMenu();
			}
		});
		}
		/* **** */
		/* END USER LOGIN MENU (NOT LOGGED IN)  */
		/* **** */

		/* **** */
		/* LOGGED-IN USER MENU ACCESSIBILITY  */
		/* **** */
		const userMenu = document.querySelector('#block-dge-basic-dge-basic-user-info-block');
		if (userMenu) {
		const trigger = userMenu.querySelector('a'); // user name link
		const submenu = userMenu.querySelector('.submenu-children');
		const links = submenu.querySelectorAll('a');
		// Init aria-expanded for accessibility
		trigger.setAttribute('aria-expanded', 'false');
		const toggleUserMenu = () => {
			const isOpen = userMenu.classList.toggle('is-visible');
			trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
		};
		const closeUserMenu = () => {
			if (userMenu.classList.contains('is-visible')) {
			userMenu.classList.remove('is-visible');
			trigger.setAttribute('aria-expanded', 'false');
			console.log('User menu closed');
			}
		};
		// Handle click on trigger
		trigger.addEventListener('click', function (e) {
			e.preventDefault(); // avoid scrolling to top
			toggleUserMenu();
		});
		// Handle keyboard on trigger
		trigger.addEventListener('keydown', function (e) {
			const isOpen = userMenu.classList.contains('is-visible');
			if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			toggleUserMenu();
			} else if (e.key === 'Escape' && isOpen) {
			closeUserMenu();
			trigger.focus();
			}
		});
		// Focus on submenu links auto-opens menu
		links.forEach(link => {
			link.addEventListener('focus', () => {
			userMenu.classList.add('is-visible');
			trigger.setAttribute('aria-expanded', 'true');
			});
		});
		// Close on outside click
		document.addEventListener('click', function (event) {
			if (!userMenu.contains(event.target)) {
			closeUserMenu();
			}
		});
		// Optional: close on Escape inside submenu
		submenu.addEventListener('keydown', function (e) {
			if (e.key === 'Escape') {
			closeUserMenu();
			trigger.focus();
			}
		});
		}
		/* **** */
		/* END - LOGGED-IN USER MENU ACCESSIBILITY  */
		/* **** */

	});

})(jQuery);
