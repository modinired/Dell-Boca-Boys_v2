/**
 * Dell Boca Vista Boys - Voice Chat
 * Speech-to-Text and Text-to-Speech functionality
 */

class VoiceChat {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSupported = this.checkSupport();
        this.voices = [];

        if (this.isSupported) {
            this.initializeSpeechRecognition();
            this.loadVoices();
        }

        console.log('🎤 Voice chat initialized:', this.isSupported ? '✅' : '❌ Not supported');
    }

    checkSupport() {
        return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    initializeSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error('Speech recognition not supported');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
            console.log('🎤 Listening...');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('🎤 Heard:', transcript);
            this.onTranscript(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI('error');

            if (event.error === 'not-allowed') {
                alert('Microphone access denied. Please allow microphone access in your browser settings.');
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI('idle');
            console.log('🎤 Stopped listening');
        };
    }

    loadVoices() {
        this.voices = this.synthesis.getVoices();

        if (this.voices.length === 0) {
            // Chrome loads voices asynchronously
            this.synthesis.onvoiceschanged = () => {
                this.voices = this.synthesis.getVoices();
                console.log(`🔊 Loaded ${this.voices.length} voices`);
            };
        }
    }

    startListening() {
        if (!this.isSupported) {
            alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (this.isListening) {
            this.stopListening();
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    speak(text, options = {}) {
        if (!text) return;

        // Stop any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Configure voice
        if (this.voices.length > 0) {
            // Try to find a good English voice
            const preferredVoice = this.voices.find(v =>
                v.lang.startsWith('en') && v.name.includes('Female')
            ) || this.voices.find(v => v.lang.startsWith('en'));

            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
        }

        utterance.rate = options.rate || 1.0;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;

        utterance.onstart = () => {
            console.log('🔊 Speaking...');
            this.updateUI('speaking');
        };

        utterance.onend = () => {
            console.log('🔊 Finished speaking');
            this.updateUI('idle');
        };

        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
        };

        this.synthesis.speak(utterance);
    }

    stopSpeaking() {
        this.synthesis.cancel();
        this.updateUI('idle');
    }

    onTranscript(text) {
        // Send to chat input
        $('#chatInput').val(text);

        // Auto-send if enabled
        if ($('#autoSendVoice').is(':checked')) {
            $('#sendButton').click();
        }
    }

    updateUI(state) {
        const $voiceBtn = $('#voiceInputBtn');
        const $speakBtn = $('#speakResponseBtn');

        switch (state) {
            case 'listening':
                $voiceBtn.html('<i class="fas fa-microphone-slash"></i> Stop')
                    .removeClass('btn-primary').addClass('btn-danger');
                break;
            case 'speaking':
                $speakBtn.html('<i class="fas fa-volume-mute"></i> Stop')
                    .removeClass('btn-success').addClass('btn-danger');
                break;
            case 'error':
                $voiceBtn.html('<i class="fas fa-exclamation-triangle"></i> Error')
                    .removeClass('btn-danger').addClass('btn-warning');
                setTimeout(() => this.updateUI('idle'), 2000);
                break;
            case 'idle':
            default:
                $voiceBtn.html('<i class="fas fa-microphone"></i> Voice Input')
                    .removeClass('btn-danger btn-warning').addClass('btn-primary');
                $speakBtn.html('<i class="fas fa-volume-up"></i> Read Aloud')
                    .removeClass('btn-danger').addClass('btn-success');
                break;
        }
    }

    getLastAssistantMessage() {
        const $messages = $('.chat-message.assistant');
        if ($messages.length > 0) {
            const $lastMessage = $messages.last();
            return $lastMessage.find('.chat-bubble').text().trim();
        }
        return '';
    }
}

// Initialize voice chat
$(document).ready(() => {
    window.voiceChat = new VoiceChat();

    // Add voice controls to chat interface
    if (window.voiceChat.isSupported) {
        const voiceControls = `
            <div class="voice-controls mt-2">
                <button class="btn btn-sm btn-primary" id="voiceInputBtn">
                    <i class="fas fa-microphone"></i> Voice Input
                </button>
                <button class="btn btn-sm btn-success ml-2" id="speakResponseBtn">
                    <i class="fas fa-volume-up"></i> Read Aloud
                </button>
                <div class="custom-control custom-checkbox d-inline-block ml-2">
                    <input type="checkbox" class="custom-control-input" id="autoSendVoice">
                    <label class="custom-control-label" for="autoSendVoice">Auto-send</label>
                </div>
            </div>
        `;

        $('.chat-card .card-footer').append(voiceControls);

        // Bind events
        $('#voiceInputBtn').on('click', () => {
            window.voiceChat.startListening();
        });

        $('#speakResponseBtn').on('click', () => {
            if (window.speechSynthesis.speaking) {
                window.voiceChat.stopSpeaking();
            } else {
                const text = window.voiceChat.getLastAssistantMessage();
                if (text) {
                    // Remove markdown formatting and emojis for better speech
                    const cleanText = text
                        .replace(/\*\*(.*?)\*\*/g, '$1')  // Bold
                        .replace(/\*(.*?)\*/g, '$1')      // Italic
                        .replace(/#{1,6}\s/g, '')         // Headers
                        .replace(/---/g, '')              // Dividers
                        .replace(/[🎩🔧📊🔒⚡🧪📚]/g, ''); // Emojis

                    window.voiceChat.speak(cleanText);
                } else {
                    alert('No message to read');
                }
            }
        });

        console.log('✅ Voice controls added to chat');
    }
});
