import os, subprocess, requests, runpod

discord_token = os.getenv('com_camenduru_discord_token')
web_uri = os.getenv('com_camenduru_web_uri')
web_token = os.getenv('com_camenduru_web_token')

file_path = "/home/camenduru/.local/lib/python3.10/site-packages/mmpose/datasets/builder.py"
sed_command = f"sed -i 's/resource\\.setrlimit(resource\\.RLIMIT_NOFILE, (soft_limit, hard_limit))/resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))/g' {file_path}"
subprocess.run(sed_command, shell=True, check=True)

def download_file(url, save_dir='/content'):
    os.makedirs(save_dir, exist_ok=True)
    file_name = url.split('/')[-1]
    file_path = os.path.join(save_dir, file_name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    return file_path

def generate(input):
    values = input["input"]
    ref_image = values["ref_image"]
    ref_video = values["ref_video"]
    ref_image = download_file(ref_image)
    ref_video = download_file(ref_video)
    command = [
        "python", "pose_align.py",
        "--imgfn_refer", ref_image,
        "--vidfn", ref_video
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