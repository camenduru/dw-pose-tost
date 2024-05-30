import os, subprocess, requests, runpod
from PIL import Image

discord_token = os.getenv('com_camenduru_discord_token')
web_uri = os.getenv('com_camenduru_web_uri')
web_token = os.getenv('com_camenduru_web_token')

file_path = "/home/camenduru/.local/lib/python3.10/site-packages/mmpose/datasets/builder.py"
sed_command = f"sed -i 's/resource\\.setrlimit(resource\\.RLIMIT_NOFILE, (soft_limit, hard_limit))/resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))/g' {file_path}"
subprocess.run(sed_command, shell=True, check=True)

def download_file(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            if save_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                img = Image.open(save_path)
                if img.format != "PNG":
                    png_path = os.path.splitext(save_path)[0] + ".png"
                    img.save(png_path, "PNG")
                    os.remove(save_path)
                    print(f"File converted to PNG and saved at {png_path}")
                    return True
                else:
                    print("File is already in PNG format")
                    return True
            else:
                print("File is not an image. No conversion needed.")
                return True
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def generate(input):
    values = input["input"]
    ref_image = values["ref_image"]
    ref_video = values["ref_video"]
    download_file(ref_image, "/content/image.png")
    download_file(ref_video, "/content/video.mp4")
    command = [
        "python", "pose_align.py",
        "--imgfn_refer", "/content/image.png",
        "--vidfn", "/content/video.mp4"
    ]
    pose_align = subprocess.run(command, capture_output=True, text=True)
    print("Standard Output:\n", pose_align.stdout)
    print("Standard Error:\n", pose_align.stderr)
    print("Return Code:", pose_align.returncode)
    result = f"/content/MusePose/assets/poses/align/img_ref_video_dance.mp4"

    response = None
    try:
        source_id = values['source_id']
        del values['source_id']
        source_channel = values['source_channel']     
        del values['source_channel']
        job_id = values['job_id']
        del values['job_id']
        files = {f"video.mp4": open(result, "rb").read()}
        payload = {"content": f"{json.dumps(values)} <@{source_id}>"}
        response = requests.post(
            f"https://discord.com/api/v9/channels/{source_channel}/messages",
            data=payload,
            headers={"authorization": f"Bot {discord_token}"},
            files=files
        )
        response.raise_for_status()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if os.path.exists(result):
            os.remove(result)

    if response and response.status_code == 200:
        try:
            payload = {"jobId": job_id, "result": response.json()['attachments'][0]['url']}
            requests.post(f"{web_uri}/api/notify", data=json.dumps(payload), headers={'Content-Type': 'application/json', "authorization": f"{web_token}"})
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            return {"result": response.json()['attachments'][0]['url']}
    else:
        return {"result": "ERROR"}

runpod.serverless.start({"handler": generate})