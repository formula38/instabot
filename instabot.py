import textwrap
import requests
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor, ImageFont
from imgurpython import ImgurClient
import private.config as config


class InstaBot:
    def __init__(self):
        self.font = ImageFont.truetype("private/fredoka.ttf", 50)
        self.wrapper = textwrap.TextWrapper(width=13)
        self.client = ImgurClient(config.client_id, config.client_secret)
        self.caption_template = Path('private/caption_template.txt').read_text().replace('#', '%23')
        self.access_token = Path('private/access_token.txt').read_text()
        self.index = int(Path('private/archive.txt').read_text())
        self.colors = [
            "#f08080",
            "#abdee6",
            "#cbaacb",
            "#ffffb5",
            "#ffccb6",
            "#f3b0c3",
            "#c6dbda",
            "#fee1eb",
            "#fed7c3",
            "#f6eac2",
            "#ecd5e3",
            "#ff96ba",
            "#ffaea5",
            "#ffc5bf",
            "#ffd8be",
            "#ffcba2",
            "#d4f0f0",
            "#8fcaca",
            "#cce2cb",
            "#b6cfb6",
            "#97c1a9",
            "#fcb9aa",
            "#ffdbcc",
            "#eceae4",
            "#a2e1db",
            "#55cbcd"
        ]

    with open('private/archive.txt', 'w') as file:
        file.write('0')

    def load_index(self):
        archive_path = Path('private/archive.txt')
        if archive_path.exists():
            try:
                return int(archive_path.read_text().strip())
            except ValueError:
                return 0
        else:
            return 0

    def generate_quote(self, quote: str):
        caption = quote.lower()
        wrapped_quote = self.wrapper.wrap(quote)
        wrapped_quote = "\n".join(wrapped_quote)

        rgb = ImageColor.getcolor(self.colors[self.index % len(self.colors)], "RGB")

        darker_rgb = self.tint(rgb, -70)
        img = Image.new("RGB", (1000, 1000), rgb)
        draw = ImageDraw.Draw(img)
        draw.text((500, 500), wrapped_quote.lower(), font=self.font, fill=darker_rgb, align='center', anchor='mm')

        img.save(f"img/{self.index}.png", "PNG")

        return caption

    def tint(self, rgb, tintPerc):
        return (
            int(rgb[0] * (1 + (tintPerc / 100))),
            int(rgb[1] * (1 + (tintPerc / 100))),
            int(rgb[2] * (1 + (tintPerc / 100))),
        )

    def upload_imgur(self, i):
        res = self.client.upload_from_path(f"img/{i}.png")
        return res['link']

    def renew_token(self):
        r_at = requests.get(
            f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={config.fb_id}&client_secret={config.fb_secret}&fb_exchange_token={self.access_token}")
        if r_at.status_code == 200:
            with open('private/access_token.txt', 'w') as f:
                f.write(r_at.json()['access_token'])

    def upload_img(self, i, ig_id, url, caption):
        r1 = requests.post(
            f"https://graph.facebook.com/v19.0/{ig_id}/media?image_url={url}&caption={caption}\n\n{self.caption_template}&access_token={self.access_token}")
        if r1.status_code != 200:
            exit(r1.json())
        return r1.json()['id']

    def post_publish(self, ig_id, creation_id):
        r2 = requests.post(
            f"https://graph.facebook.com/v19.0/{ig_id}/media_publish?creation_id={creation_id}&access_token={self.access_token}")
        if r2.status_code != 200:
            exit(r2.json())

    def post_image(self, url, i, caption):
        self.renew_token()
        post_id = self.upload_img(i, config.ig_id, url, caption)
        print("POST IMAGE")
        self.post_publish(config.ig_id, post_id)

    def parse_sheets(self):
        test = pd.read_csv(config.script_link)
        q = test.loc[self.index, 'quote']
        with open('private/archive.txt', 'w') as f:
            f.write(str(self.index + 1))
        return q

    def run(self):
        caption = self.generate_quote(self.parse_sheets())
        link = self.upload_imgur(self.index)
        print(link)
        self.post_image(link, self.index, caption)


if __name__ == '__main__':
    bot = InstaBot()
    bot.run()
