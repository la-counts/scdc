function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

function eraseCookie(name) {
	createCookie(name,"",-1);
}

$(document).ready(function() {
    $(".user-icon").on("click", function(){
        $(".user-nav").slideToggle(100);
    });

    $(".user-icon").mouseleave ( function(){
        var menu = $(".user-nav");
        if (menu.is(':visible')) {
            menu.slideUp(100);
        }
    });

    $(".hello").on("click", function(){
        $(".hello-menu").slideToggle(100);
    });

    $(".hello-menu").mouseleave ( function(){
        var menu = $(".hello-menu");
        if (menu.is(':visible')) {
            menu.slideUp(100);
        }
    });

    /* Trigger re-search */
    var submitForm = function() {
      $(this).parents('form').submit()
    }

    $('.search_results_wrapper :input').blur(submitForm);
    $('.search_results_wrapper select').change(submitForm);
    $('.search_results_wrapper input[type="checkbox"]').change(submitForm);

    if ($('.publisher-expand-icons')) {
        $('.publisher-expand-icons > i').on('click', function(e) {
            e.preventDefault();
            var me = $(this);
            var parent = me.closest('.publisher-item');
            parent.toggleClass('opened');
        })
    }

    if ($('.search-group-title')) {
        $('.search-group-title').on('click', function(e) {
            e.preventDefault();
            var me = $(this);
            var parent = me.parent();
            parent.toggleClass('opened');
        });
    }

    //Demo only
    if ($('.demo-progress-slider')) {
        var progressBarWrapper = $('.progress-wrapper');
        $('.demo-progress-slider').on('input', function(e) {
            var me = $(this);
            var myVal = me.val();
            var bar = progressBarWrapper.find('.progress-bar');
            bar.attr('aria-valuenow', myVal).width(myVal+'%');
            bar.find('.sr-only').text(myVal+'% complete');
            var progressNumber = progressBarWrapper.find('.percentage > span');
            progressNumber.text(myVal);
        })
    }
    
    if (($('body').hasClass('not-logged-in') && $('body').hasClass('home-page')) && $('#homepage_modal_wrapper').length == 1) {
        var modalHasBeenClosed = parseInt(readCookie('modalclosed'));
        var homepageModal = $('#homepage_modal_wrapper');
        
        if (modalHasBeenClosed !== 1) {
            $('body').addClass('modal-open');
            homepageModal.find('[data-modal="close"]').on('click', function(e) {
                e.preventDefault();
                homepageModal.fadeOut('fast');
                $('body').removeClass('modal-open');
                
                //Set Cookie on Close.
                createCookie('modalclosed', 1);
            });
        } else {
            if (homepageModal.is(':visible')) {
                homepageModal.hide();
                $('body').removeClass('modal-open');
            }
        }
    }
	
	$('.saved-status-unregistered > a').on('click', function(e) {
		e.preventDefault();
		$('body').addClass('save-modal-open');
	});
	
	$('#save_modal_link, #save_modal_wrapper .modal-button[data-modal="close"]').on('click', function(e) {
		e.preventDefault();
		$('body').removeClass('save-modal-open');
	})
    
    $('.widget-panel-anchor-link').on('click', function(e) {
        e.preventDefault();
        var me = $(this);
        var myLink = me.attr('href').replace('#', '');
        
        var tab = $('[data-tab="'+myLink+'"]');
        if (tab.length) {
            if (tab.is(':visible')) {
                tab.hide();
            } else {
                //Hide other tabs!
                $('[data-tab]').not(tab).hide();
                tab.show();
            }
        }
    });
    
    function alphaCheckGroups() {
        var alphaGroups = $('.alpha-publisher-group');
        
        $.each(alphaGroups, function() {
            var thisGroup = $(this);
            var groupItems = thisGroup.find('.publisher-list > li');
            var hiddenItems = thisGroup.find('.publisher-list > li.hidden');
            if (groupItems.length == hiddenItems.length) {
                thisGroup.hide();
            } else {
                //thisGroup.css('display', 'block');
				thisGroup.show();
            }
        });
    }
	
	function reorderAlphaGroupExceptions() {
        var alphaGroups_c = $('.alpha-publisher-group[data-letter="C"]');
		var li = alphaGroups_c.find('li[data-name="California, State of"]');
		li.parent().prepend(li);
		
		li = alphaGroups_c.find('li[data-name="CalFish"]');
		li.parent().prepend(li);
    }
    
	reorderAlphaGroupExceptions();
	
    $('.filter-controls a').on('click', function(e) {
        e.preventDefault();
        var me = $(this);
        var filter = me.attr('data-filter');
        if (filter == "all") {
            //Select all
            $('.filter-inputs input[type="checkbox"]').prop('checked', true);
            $('.publisher-listing-grouped .publisher-list > li').removeClass('hidden');
        } else {
            //Select none!
            $('.filter-inputs input[type="checkbox"]').prop('checked', false);
            $('.publisher-listing-grouped .publisher-list > li').addClass('hidden');
        }
        
        alphaCheckGroups();
    });
    
    $('.filter-inputs input[type="checkbox"]').on('change', function() {
        var me = $(this);
        var filter = me.attr('data-filter');
        var checked = me.prop('checked');
        
        if (checked) {
            $('.publisher-listing-grouped .publisher-list > li[data-filter="'+filter+'"]').removeClass('hidden');
        } else {
            $('.publisher-listing-grouped .publisher-list > li[data-filter="'+filter+'"]').addClass('hidden');
        }
        
        alphaCheckGroups();
    });
    
    $('.publisher-listing-alphabet a').on('click', function(e) {
        e.preventDefault();
        var me = $(this);
        var letter = me.attr('data-letter').toUpperCase();
        var anchor = $('a[name="alpha_'+letter+'"]');
        if (anchor.length) {
            //Scroll to it.
            $('html, body').animate({
                scrollTop: (anchor.offset().top - 135)
            }, 800);
        }
    });
    
    if ($('#back-to-top').length) {
        var scrollTrigger = 200, // px
            backToTop = function () {
                var scrollTop = $(window).scrollTop();
                if (scrollTop > scrollTrigger) {
                    $('#back-to-top').addClass('show');
                } else {
                    $('#back-to-top').removeClass('show');
                }
            };
        
        backToTop();
        
        $(window).on('scroll', function () {
            backToTop();
        });
        
        $('#back-to-top').on('click', function (e) {
            e.preventDefault();
            $('html,body').animate({
                scrollTop: 0
            }, 700);
        });
    }
    
    $('.collapsible-section .collapsible-title').on('click', function(e) {
        e.preventDefault();
        var me = $(this);
        var section = me.parent();
        $('.collapsible-section').not(section).removeClass('open');
        section.toggleClass('open');
        
        if (section.hasClass('open')) {
            $('.collapsible-text').slideUp('fast');
            section.find('.collapsible-text').slideDown('fast');
        } else {
            section.find('.collapsible-text').slideUp('fast');
        }
    });
    
    setTimeout(function() {
        $('.publishers-tabs > div').hide().css('opacity', 1);
    }, 100);
    
    $('.featured-content-image-slides').slick({
		autoplay: true,
		autoplaySpeed: 5000,
        prevArrow: '<button class="left carousel-control"><img src="/static/images/carousel-nav-prev.svg"></button>',
        nextArrow: '<button class="right carousel-control"><img src="/static/images/carousel-nav-next.svg"></button>',
        dots: true,
    });
    
    if ($('#id_display_name').length) {
        $('#id_display_name').focus();
    }
    
    if ($('#avatar_button_overlay').length) {
        $('#avatar_button_overlay, .avatar-image').on('click', function(e) {
            e.preventDefault();
            $('#id_avatar').click();
        });
    }
    
    $('.meta-accordion-icon').on('click', function() {
        var me = $(this);
        var accordion = me.parent();
        var isOpen = (accordion.attr('data-open') === "open");
        if (isOpen) {
            accordion.attr('data-open', '');
        } else {
            accordion.attr('data-open', 'open');
        }
    });
    
    //Temporary
    setTimeout(function() {
        $('label[for="id_username"]').html('Email');
        $('#id_username').attr('placeholder','Email');
    }, 0);
    
    var hasModalBeenClosed = readCookie('modalclosed');
    if (null === hasModalBeenClosed) {
        //Never seen the cookie... create it.
        createCookie('modalclosed', 0);
    }
});

/*mobile menu*/

$(document).ready(function() {
    $(".mobile-trigger, .close-icon").on("click",function() {
        $(".mobile-main-menu").toggleClass('move');
    });
});

/* recent activity */
var MAX_RECENTLY_VIEWED = 5
function pushRecentView(slot, info) {
  var currentViews = window.localStorage.getItem(slot)
  if (currentViews) {
    try {
      currentViews = JSON.parse(currentViews)
    } catch (e){
      currentViews = []
    }
  } else {
    currentViews = []
  }
  if (currentViews.length >= MAX_RECENTLY_VIEWED) {
    currentViews = currentViews.slice(0, MAX_RECENTLY_VIEWED - 1)
  }
  //dedupe recent activity based on url
  if (currentViews.length && currentViews[0].url === info.url) {
    return
  }
  currentViews.splice(0, 0, info)
  window.localStorage.setItem(slot, JSON.stringify(currentViews))
}

function getRecentViews(slot) {
  var currentViews = window.localStorage.getItem(slot)
  try {
    return JSON.parse(currentViews)
  } catch (e){
    return []
  }
}
