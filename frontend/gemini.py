import os
import time
import google.generativeai as genai

genai.configure(api_key="AIzaSyAKIuj0Kz-76o5Nl8zTxuG1nHpWDR5PKJQ")

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

# TODO Make these files available on the local file system
# You may need to update the file paths
# files = [
#   upload_to_gemini("output_folder/motion_clip_1729358663.mp4", mime_type="video/mp4"),
# ]

# Some files have a processing delay. Wait for them to be ready.
# wait_for_files_active(files)




# response = chat_session.send_message("Pretend like the video is a view from a security camera. Give a quick alert messages that is less than 10 words that says what is happening in the video.")

# print(response.text)

def generate_alert_message(video_path):
    print("point 1", video_path)
    files = [
        upload_to_gemini(f"./{video_path}", mime_type="video/mp4"),
    ]

    wait_for_files_active(files)

    print(files)

    chat_session = model.start_chat(
    history=[
      {
        "role": "user",
        "parts": [
          files[0],
        ],
      },
      {
        "role": "user",
        "parts": [
          "What is happening in this video? Pretend like video is coming from a security camera from a home doorbell. Generate a quick security alert message. Make sure that the message is less than 10 words. Start the message with 'Alert:'.",
        ],
      },
    ]
  )

    prompt = (f"What is happening in this video? Generate a quick security alert message. Make sure that the message is less than 10 words. Start the message with 'Alert:'.")


    response = chat_session.send_message(prompt)


    return response.text