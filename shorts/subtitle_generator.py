import re
from datetime import timedelta


def format_timestamp(seconds):
    """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    ts = str(timedelta(seconds=seconds)).replace('.', ',')

    # Ensure it has milliseconds
    if ',' not in ts:
        ts += ',000'
    else:
        # Ensure 3 decimal places for milliseconds
        parts = ts.split(',')
        ts = f"{parts[0]},{parts[1][:3].ljust(3, '0')}"

    # Format to ensure proper SRT timestamp format (HH:MM:SS,mmm)
    if len(ts.split(':')) == 2:
        ts = f"00:{ts}"

    return ts


def create_word_by_word_subtitle_file(transcript_data, start_time, end_time, output_file="subtitles.srt", words_per_subtitle=2):
    """Create SRT subtitle file with word-by-word or few words at a time display"""
    with open(output_file, 'w', encoding='utf-8') as f:
        counter = 1

        # Filter transcript entries within our segment
        segment_transcript = [
            entry for entry in transcript_data
            if entry['start'] >= start_time and entry['start'] < end_time
        ]

        for entry in segment_transcript:
            # Calculate relative time within the segment
            rel_start = entry['start'] - start_time
            rel_end = min(entry['start'] + entry['duration'],
                          end_time) - start_time
            duration = rel_end - rel_start

            # Split the text into words
            words = re.findall(r'\b\w+\b|\S', entry['text'])

            # Group words into smaller chunks
            chunks = []
            current_chunk = []

            for word in words:
                current_chunk.append(word)
                if len(current_chunk) >= words_per_subtitle:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []

            # Add any remaining words
            if current_chunk:
                chunks.append(' '.join(current_chunk))

            # Calculate time per chunk
            time_per_chunk = duration / len(chunks) if chunks else duration

            # Create subtitles for each chunk
            for i, chunk in enumerate(chunks):
                chunk_start = rel_start + (i * time_per_chunk)
                chunk_end = rel_start + ((i + 1) * time_per_chunk)

                # Format timestamps
                start_ts = format_timestamp(chunk_start)
                end_ts = format_timestamp(chunk_end)

                # Write subtitle entry
                f.write(f"{counter}\n")
                f.write(f"{start_ts} --> {end_ts}\n")
                f.write(f"{chunk}\n\n")
                counter += 1

    return output_file
