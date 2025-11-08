/**
 * Dell Boca Vista Boys - Screen Recording
 * Screen capture with audio and automatic summary generation
 */

class ScreenRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.startTime = null;
        this.timerInterval = null;
        this.recordings = [];

        this.isSupported = this.checkSupport();
        console.log('📹 Screen recorder initialized:', this.isSupported ? '✅' : '❌ Not supported');
    }

    checkSupport() {
        return 'mediaDevices' in navigator && 'getDisplayMedia' in navigator.mediaDevices;
    }

    async startRecording() {
        if (!this.isSupported) {
            alert('Screen recording is not supported in your browser. Please use Chrome, Edge, or Firefox.');
            return;
        }

        if (this.isRecording) {
            this.stopRecording();
            return;
        }

        try {
            // Request screen capture
            this.stream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: 'always',
                    displaySurface: 'monitor'
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });

            // Create media recorder
            const options = {
                mimeType: 'video/webm;codecs=vp9',
                videoBitsPerSecond: 2500000  // 2.5 Mbps
            };

            // Fallback for Safari
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'video/webm';
            }

            this.mediaRecorder = new MediaRecorder(this.stream, options);
            this.recordedChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.handleRecordingStop();
            };

            // Handle stream stop (user clicks browser's stop button)
            this.stream.getVideoTracks()[0].addEventListener('ended', () => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            });

            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            this.startTime = Date.now();

            this.startTimer();
            this.updateUI('recording');

            console.log('📹 Recording started');

        } catch (error) {
            console.error('Failed to start recording:', error);
            if (error.name === 'NotAllowedError') {
                alert('Screen recording permission denied.');
            } else {
                alert(`Failed to start recording: ${error.message}`);
            }
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;

            // Stop all tracks
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            this.stopTimer();
            console.log('📹 Recording stopped');
        }
    }

    handleRecordingStop() {
        const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
        const duration = Math.floor((Date.now() - this.startTime) / 1000);

        const recording = {
            id: Date.now(),
            blob: blob,
            url: URL.createObjectURL(blob),
            timestamp: new Date().toISOString(),
            duration: duration,
            size: blob.size
        };

        this.recordings.push(recording);
        this.updateUI('stopped');

        // Show recording result
        this.showRecordingResult(recording);

        // Auto-generate summary
        this.generateSummary(recording);
    }

    showRecordingResult(recording) {
        const minutes = Math.floor(recording.duration / 60);
        const seconds = recording.duration % 60;
        const sizeMB = (recording.size / (1024 * 1024)).toFixed(2);

        const html = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <h5><i class="fas fa-check-circle"></i> Recording Saved</h5>
                <p>
                    <strong>Duration:</strong> ${minutes}m ${seconds}s<br>
                    <strong>Size:</strong> ${sizeMB} MB<br>
                    <strong>Time:</strong> ${new Date(recording.timestamp).toLocaleTimeString()}
                </p>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-primary" onclick="window.screenRecorder.playRecording(${recording.id})">
                        <i class="fas fa-play"></i> Play
                    </button>
                    <button class="btn btn-success" onclick="window.screenRecorder.downloadRecording(${recording.id})">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-info" onclick="window.screenRecorder.viewSummary(${recording.id})">
                        <i class="fas fa-file-alt"></i> Summary
                    </button>
                </div>
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `;

        $('#recordingResults').prepend(html);
    }

    playRecording(id) {
        const recording = this.recordings.find(r => r.id === id);
        if (!recording) return;

        // Create video player modal
        const modal = `
            <div class="modal fade" id="videoModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Recording Playback</h5>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <video controls style="width: 100%;">
                                <source src="${recording.url}" type="video/webm">
                            </video>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modal);
        $('#videoModal').modal('show');
        $('#videoModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    downloadRecording(id) {
        const recording = this.recordings.find(r => r.id === id);
        if (!recording) return;

        const a = document.createElement('a');
        a.href = recording.url;
        a.download = `dell-boca-vista-recording-${new Date(recording.timestamp).toISOString().slice(0, 19).replace(/:/g, '-')}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        console.log('📹 Download started');
    }

    async generateSummary(recording) {
        console.log('📝 Generating summary for recording...');

        try {
            const response = await fetch('/api/recording/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recording_id: recording.id,
                    duration: recording.duration,
                    timestamp: recording.timestamp
                })
            });

            const data = await response.json();
            recording.summary = data.summary;

            console.log('✅ Summary generated');

        } catch (error) {
            console.error('Failed to generate summary:', error);
            recording.summary = 'Summary generation unavailable';
        }
    }

    viewSummary(id) {
        const recording = this.recordings.find(r => r.id === id);
        if (!recording) return;

        const summary = recording.summary || 'Generating summary...';

        const modal = `
            <div class="modal fade" id="summaryModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Recording Summary</h5>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <h6>Recording Details</h6>
                            <p>
                                <strong>Date:</strong> ${new Date(recording.timestamp).toLocaleString()}<br>
                                <strong>Duration:</strong> ${Math.floor(recording.duration / 60)}m ${recording.duration % 60}s<br>
                                <strong>Size:</strong> ${(recording.size / (1024 * 1024)).toFixed(2)} MB
                            </p>
                            <hr>
                            <h6>AI-Generated Summary</h6>
                            <div class="summary-content">
                                ${summary}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="window.screenRecorder.regenerateSummary(${id})">
                                <i class="fas fa-redo"></i> Regenerate
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        $('body').append(modal);
        $('#summaryModal').modal('show');
        $('#summaryModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    }

    async regenerateSummary(id) {
        const recording = this.recordings.find(r => r.id === id);
        if (!recording) return;

        $('#summaryModal .summary-content').html('<div class="loading"></div> Regenerating summary...');

        await this.generateSummary(recording);

        $('#summaryModal .summary-content').html(recording.summary);
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            $('#recordingTimer').text(`${minutes}:${seconds.toString().padStart(2, '0')}`);
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        $('#recordingTimer').text('0:00');
    }

    updateUI(state) {
        const $recordBtn = $('#recordScreenBtn');

        switch (state) {
            case 'recording':
                $recordBtn.html('<i class="fas fa-stop-circle"></i> Stop Recording')
                    .removeClass('btn-danger').addClass('btn-danger');
                $('#recordingIndicator').show();
                break;
            case 'stopped':
            default:
                $recordBtn.html('<i class="fas fa-video"></i> Record Screen')
                    .removeClass('btn-danger').addClass('btn-primary');
                $('#recordingIndicator').hide();
                break;
        }
    }

    getAllRecordings() {
        return this.recordings;
    }
}

// Initialize screen recorder
$(document).ready(() => {
    window.screenRecorder = new ScreenRecorder();

    // Add recording controls to dashboard
    const recordingSection = `
        <div class="card mt-3" id="recordingSection">
            <div class="card-header">
                <h5><i class="fas fa-video"></i> Screen Recording & Summary Reviews</h5>
            </div>
            <div class="card-body">
                <div class="recording-controls">
                    <button class="btn btn-primary" id="recordScreenBtn">
                        <i class="fas fa-video"></i> Record Screen
                    </button>
                    <span class="ml-3" id="recordingIndicator" style="display: none;">
                        <span class="badge badge-danger">
                            <i class="fas fa-circle" style="animation: pulse 1.5s infinite;"></i>
                            REC <span id="recordingTimer">0:00</span>
                        </span>
                    </span>
                </div>
                <div id="recordingResults" class="mt-3">
                    <!-- Recording results will appear here -->
                </div>
            </div>
        </div>
    `;

    // Add to appropriate page
    if ($('#page-dashboard .container-fluid').length) {
        $('#page-dashboard .container-fluid').append(recordingSection);
    }

    // Bind events
    $('#recordScreenBtn').on('click', () => {
        if (window.screenRecorder.isRecording) {
            window.screenRecorder.stopRecording();
        } else {
            window.screenRecorder.startRecording();
        }
    });

    console.log('✅ Screen recording controls added');
});
