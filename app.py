# 4. Engine Run Pipeline Logic
if process_btn:
    if not url_input:
        strl.error("Configuration Execution Blocked: Link String Missing.")
    else:
        try:
            strl.session_state.download_status = "Analyzing Target..."
            strl.session_state.download_progress = 0.0
            clean_old_files()
            
            # WORKAROUND: Forcing fallback streams and enabling proxy hooks if available
            meta_opts = {
                'quiet': True, 
                'no_warnings': True,
                'cachedir': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'tv'],
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                meta = ydl.extract_info(url_input, download=False)
            
            with right_col:
                strl.markdown(f"""
                    <div class='dashboard-card' style='border-color: #3B82F6;'>
                        <b>Title:</b> {meta.get('title', 'Unknown')}<br>
                        <b>Creator:</b> {meta.get('uploader', 'Unknown')}<br>
                        <b>Length:</b> {time.strftime('%H:%M:%S', time.gmtime(meta.get('duration', 0)))}
                    </div>
                """, unsafe_allow_html=True)
            
            # Use single-format delivery blocks to prevent 403 authorization failures
            ydl_opts = {
                'outtmpl': 'downloaded_media.%(ext)s',
                'progress_hooks': [progress_callback],
                'quiet': True,
                'no_warnings': True,
                'cachedir': False,
                # Pull single complete file structures directly rather than separate streams
                'format': 'best[ext=mp4]/best', 
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'tv'],
                        'skip': ['dash', 'hls']
                    }
                }
            }

            if media_format == "Audio Only (MP3)":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality.replace("kbps", ""),
                    }]
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_input])
                
            output_file_path = get_output_file()
            
            if output_file_path and os.path.exists(output_file_path):
                p_bar.progress(1.0)
                strl.session_state.download_status = "Finished Stream Transfer"
                strl.toast("Transcoding Process Completed!", icon="🎉")
                
                with open(output_file_path, "rb") as final_data:
                    binary_payload = final_data.read()
                    
                ext_lbl = "mp3" if media_format == "Audio Only (MP3)" else "mp4"
                
                with left_col:
                    strl.download_button(
                        label=f"📥 RETRIEVE COMPLETED .{ext_lbl.upper()} FILE",
                        data=binary_payload,
                        file_name=f"Download_{int(time.time())}.{ext_lbl}",
                        mime="audio/mpeg" if ext_lbl == "mp3" else "video/mp4"
                    )
        except Exception as system_fault:
            strl.error(f"Error Processing Subsystem Chain: {str(system_fault)}")
            strl.session_state.download_status = "Pipeline Halted"
