class Content {
    constructor() {
        this.maxVolume = 600;
        this.vizualizeContent = null;
        this._fadeInterval = null;
        this._fadeTimeout = null;
        this.gainNode = null;
        this.updateVolume = this.updateVolume.bind(this);
        this.run();
    }

    run() {
        this.initListeners();
        this.createHtml();
    }

    initListeners() {
        setTimeout(() => this.initMessageListeners(), 1000); // Fixed setTimeout
    }

    initMessageListeners() {
        chrome.runtime.onMessage.addListener((e, t, s) => {
            switch (e.action) {
                case "showGain":
                    this.updateVolume(e.volume);
                    break;
                default:
                    console.log('Unknown action:', e.action);
            }
        });
    }

    createHtml() {
        let audioElement = document.createElement("audio");
        audioElement.classList.add("audio-output");
        audioElement.style.display = "none";
        document.body.appendChild(audioElement);

        if (!this.vizualizeContent) {
            const visualizerHTML = `
                <div id="volume-booster-visusalizer">
                    <div class="sound">
                        <div class="sound-icon"></div>
                        <div class="sound-wave sound-wave_one"></div>
                        <div class="sound-wave sound-wave_two"></div>
                        <div class="sound-wave sound-wave_three"></div>
                    </div>
                    <div class="segments-box">
                        <div data-range="1-20" class="segment"><span></span></div>
                        <div data-range="21-40" class="segment"><span></span></div>
                        <div data-range="41-60" class="segment"><span></span></div>
                        <div data-range="61-80" class="segment"><span></span></div>
                        <div data-range="81-100" class="segment"><span></span></div>
                    </div>
                </div>
            `;
            
            // Using jQuery if available, fallback to vanilla JS
            if (typeof $ !== 'undefined') {
                this.vizualizeContent = $(visualizerHTML);
                this.vizualizeContent.appendTo("body");
            } else {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = visualizerHTML;
                this.vizualizeContent = tempDiv.firstElementChild;
                document.body.appendChild(this.vizualizeContent);
            }
        }
    }

    updateVolume(volume) {
        const volumeValue = +volume;
        if (Number.isInteger(volumeValue)) {
            const percentage = parseInt(100 * volumeValue / this.maxVolume);
            
            // Show visualizer
            if (typeof $ !== 'undefined') {
                this.vizualizeContent.css({
                    display: "flex",
                    opacity: 1
                });
            } else {
                this.vizualizeContent.style.display = "flex";
                this.vizualizeContent.style.opacity = 1;
            }

            clearInterval(this._fadeInterval);
            clearTimeout(this._fadeTimeout);
            this.updateSegments(percentage);
            
            // Toggle mute class
            const soundElement = this.vizualizeContent.querySelector(".sound");
            if (soundElement) {
                soundElement.classList.toggle("sound-mute", percentage < 1);
            }

            this.hideVisualizer();
        }
    }

    updateSegments(percentage) {
        const segments = this.vizualizeContent.querySelectorAll(".segment");
        segments.forEach(segment => {
            const span = segment.querySelector("span");
            const range = segment.dataset.range.split("-");
            const min = +range[0];
            const max = +range[1];

            if (percentage > max) {
                span.style.height = "100%";
            } else if (percentage >= min && percentage <= max) {
                span.style.height = `${100 - 100 * (max - percentage) / 20}%`;
            } else {
                span.style.height = "0";
            }
        });
    }

    hideVisualizer() {
        this._fadeTimeout = setTimeout(() => {
            this._fadeInterval = setInterval(() => {
                const currentOpacity = parseFloat(this.vizualizeContent.style.opacity) || 1;
                const newOpacity = currentOpacity - 0.01;
                
                if (newOpacity > 0) {
                    this.vizualizeContent.style.opacity = newOpacity;
                } else {
                    this.vizualizeContent.style.display = "none";
                    clearInterval(this._fadeInterval);
                }
            }, 10);
        }, 800);
    }
}

// Initialize only if we're in a browser context
if (typeof window !== 'undefined') {
    const content = new Content();
}
