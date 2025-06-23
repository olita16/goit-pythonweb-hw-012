import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Сервіс для завантаження файлів у Cloudinary.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Ініціалізує параметри підключення до Cloudinary.

        :param cloud_name: Назва облікового запису в Cloudinary.
        :param api_key: API ключ.
        :param api_secret: API секрет.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантажує файл користувача в Cloudinary та формує URL.

        :param file: Об'єкт файлу (типу UploadFile).
        :param username: Ім’я користувача для формування public_id.
        :return: Посилання на завантажене зображення (250x250).
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
