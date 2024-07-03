const UPDATE_POPUP_POSITION_INTERVAL_MS = 100;
// Kinda useless as we use "run_at": "document_end", in manifest.json.
const OBSERVE_VIDEOS_TIMEOUT_MS = 50;
const FETCH_VIDEO_INFO_TIMEOUT_MS = 50;

const createPopup = () => {
    const popupElement = document.createElement('div');
    popupElement.style.position = 'fixed';
    popupElement.style.zIndex = '1000';
    popupElement.style.width = 'auto';
    popupElement.style.background = 'white';
    popupElement.style.border = '1px solid black';
    popupElement.style.borderRadius = '8px';
    popupElement.style.padding = '16px';
    popupElement.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    popupElement.style.display = 'none';
    popupElement.style.fontSize = '16px';
    document.body.appendChild(popupElement);
    return popupElement;
};

const updatePopup = (popup, summary, rating, tldrComments) => {
    // Clean loading.
    popup.innerHTML = '';
    // Insert new content.
    const summaryHtml = document.createElement('div');
    summaryHtml.innerHTML = `<strong>Summary:</strong> ${summary}<br>`;
    const ratingHtml = document.createElement('div');
    ratingHtml.innerHTML = `<strong>Rating:</strong> ${rating}<br>`;
    const tldrCommentsHtml = document.createElement('div');
    tldrCommentsHtml.innerHTML = `<strong>TLDR Comments:</strong> ${tldrComments}<br>`;
    popup.appendChild(summaryHtml);
    popup.appendChild(ratingHtml);
    popup.appendChild(tldrCommentsHtml);
};

const throttle = (func, limit) => {
    let lastFunc;
    let lastRan;
    return function() {
        const context = this;
        const args = arguments;
        if (!lastRan) {
            func.apply(context, args);
            lastRan = Date.now();
        } else {
            clearTimeout(lastFunc);
            lastFunc = setTimeout(function() {
                if ((Date.now() - lastRan) >= limit) {
                    func.apply(context, args);
                    lastRan = Date.now();
                }
            }, limit - (Date.now() - lastRan));
        }
    };
};

// TODO
const fetchVideoInfo = async (url) => {
    console.log('Fetch info from url', url)
    return "descriptiondescriptiondescription\n" +
        "descriptiondescriptiondescriptiondescription"
};

(function() {
    'use strict';

    const popup= createPopup();

    const showLoadingPopup = (popup, x, y) => {
        popup.innerHTML = '<strong>Loading...</strong>';
        popup.style.left = `${x}px`;
        popup.style.top = `${y}px`;
        popup.style.display = 'block';
    };

    const observeDOM = () => {

        const observer = new MutationObserver((mutations, obs) => {
            setTimeout(() => {
                const channelElements = document.querySelectorAll('#video-preview');
                if (channelElements.length) {
                    addEventListners(channelElements);
                    obs.disconnect();
                }
            }, OBSERVE_VIDEOS_TIMEOUT_MS);
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    };

    const addEventListners = (channelElements) => {
        channelElements.forEach(channelElement => {
            let popupTimeout;

            channelElement.addEventListener('mouseenter', async (e) => {
                clearTimeout(popupTimeout);
                popupTimeout = setTimeout(async () => {
                    const url = channelElement.querySelector('a').href;
                    showLoadingPopup(popup, e.clientX, e.clientY + 20);
                    const content = await fetchVideoInfo(url);
                    updatePopup(popup, "DescriptionDescriptionDescription", "RatingRatingRating", "TLDR CommentsTLDR CommentsTLDR Comments");
                }, FETCH_VIDEO_INFO_TIMEOUT_MS);
            });

            channelElement.addEventListener('mouseleave', () => {
                clearTimeout(popupTimeout);
                popup.style.display = 'none';
            });

            const throttledMouseMove = throttle((e) => {
                if (popup.style.display !== 'none') {
                    popup.style.left = `${e.clientX}px`;
                    popup.style.top = `${e.clientY + 20}px`;
                }
            }, UPDATE_POPUP_POSITION_INTERVAL_MS);

            channelElement.addEventListener('mousemove', throttledMouseMove);
        });
    };

    observeDOM();
})();