/*
* Copyright (C) 2026 Entidad Pública Empresarial Red.es
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

ckan.module('dge-cookies', function ($) {

  return {

    options: {
      hostname: null,
      domain: null,
      protocol: null
    },

    initialize: function () {
      var self = this;

      /* ==========================
         COOKIE HELPERS
      ========================== */

      function getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) {
          return decodeURIComponent(parts.pop().split(";").shift());
        }
        return null;
      }

      function parseConsent() {
        const raw = getCookie("cookiesjsr");
        if (!raw) return null;

        try {
          return JSON.parse(raw);
        } catch (e) {
          console.error("Cookie cookiesjsr inválida", e);
          return null;
        }
      }

      function hasDecision(consent) {
        return consent && typeof consent.analytics === "boolean";
      }

      function setConsent(consent) {

        let cookie =
          "cookiesjsr=" + encodeURIComponent(JSON.stringify(consent)) +
          "; Path=/; SameSite=Lax";

       

        if (location.protocol === self.options.protocol) {
          cookie += "; Secure";
        }

        document.cookie = cookie;

        hideBanner();
        enableServices(consent);
      }

      /* ==========================
         GOOGLE ANALYTICS
      ========================== */

      function hasAnalyticsConsent() {
        const consent = parseConsent();
        return consent && consent.analytics === true;
      }

      function loadGA() {
        if (window.gaLoaded) return;
        window.gaLoaded = true;

        const configEl = document.getElementById("ga-config");
        if (!configEl) return;

        const gaId = configEl.dataset.gaId;
        if (!gaId) return;

        const script1 = document.createElement('script');
        script1.async = true;
        script1.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
        document.head.appendChild(script1);

        const script2 = document.createElement('script');
        script2.innerHTML = `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${gaId}');
        `;
        document.head.appendChild(script2);
      }

      function initGAFromConsent() {
        if (hasAnalyticsConsent()) {
          loadGA();
        }
      }

      /* ==========================
         SERVICE ENABLING
      ========================== */

      function enableServices(consent) {
        if (!consent) return;

        if (consent.analytics) {
          loadGA();
        }

        if (consent.youtube_video) {
          window.enableYouTube && window.enableYouTube();
        }

        if (consent.vimeo_video) {
          window.enableVimeo && window.enableVimeo();
        }

        if (consent.powerbi_embed) {
          window.enablePowerBI && window.enablePowerBI();
        }
      }

      /* ==========================
         UI
      ========================== */

      function showBanner() {
        $("#cookies-banner").removeClass("hidden");
      }

      function hideBanner() {
        $("#cookies-banner").addClass("hidden");
      }

      /* ==========================
         INIT
      ========================== */

      const consent = parseConsent();

      if (!hasDecision(consent)) {
        showBanner();
      } else {
        enableServices(consent);
      }

      /* ==========================
         EVENTS
      ========================== */

      $("#cookies-accept").on("click", function () {
        setConsent({
          functional: true,
          analytics: true,
          youtube_video: true,
          vimeo_video: true,
          powerbi_embed: true
        });
      });

      $("#cookies-reject").on("click", function () {
        setConsent({
          functional: false,
          analytics: false,
          youtube_video: false,
          vimeo_video: false,
          powerbi_embed: false
        });
      });

       $("#cookies-layer-accept").on("click", function () {
        setConsent({
          functional: true,
          analytics: true,
          youtube_video: true,
          vimeo_video: true,
          powerbi_embed: true
        });
        $("#cookiesjsr-layer-wrapper").addClass("hidden");
      });

      $("#cookies-layer-reject").on("click", function () {
        setConsent({
          functional: false,
          analytics: false,
          youtube_video: false,
          vimeo_video: false,
          powerbi_embed: false
        });
        $("#cookiesjsr-layer-wrapper").addClass("hidden");
      });


      $(".cookiesjsr-service-group--tab").on("click", function () {

        // Quitar active de todos los grupos
        $(".cookiesjsr-service-group").removeClass("active");

        // Añadir active al grupo padre del botón clicado
        $(this).closest(".cookiesjsr-service-group").addClass("active");

        $(".cookiesjsr-service-group--tab").attr("aria-selected", "false");
        $(this).attr("aria-selected", "true");
      });


      $("#cookies-layer-save").on("click", function () {

        const consent = {
          functional: false,
          analytics: false,
          youtube_video: false,
          vimeo_video: false,
          powerbi_embed: false
        };

        $(".consent-slider").each(function () {
          const service = $(this).data("service");
          consent[service] = $(this).is(":checked");
        });

        setConsent(consent);
        $("#cookiesjsr-layer-wrapper").addClass("hidden");
      });

      $("#cookies-settings").on("click", function () {
        $("#cookiesjsr-layer-wrapper").removeClass("hidden");
      });

      $("#cookies-layer-close").on("click", function () {
        $("#cookiesjsr-layer-wrapper").addClass("hidden");
      });

      $(".cookiesjsr-layer--overlay").on("click", function () {
        $("#cookiesjsr-layer-wrapper").addClass("hidden");
      });

      initGAFromConsent();

    }
  };
});