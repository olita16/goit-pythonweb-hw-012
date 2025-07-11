import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Сервіс для завантаження файлів на Cloudinary.

    Ініціалізується з параметрами доступу до Cloudinary.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Ініціалізація Cloudinary з конфігурацією.

        Args:
            cloud_name (str): Ім'я Cloudinary облікового запису.
            api_key (str): API ключ.
            api_secret (str): Секретний ключ.
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
    def upload_file(file, username: str) -> str:
        """
        Завантажує файл на Cloudinary та повертає URL зображення.

        Args:
            file: Об'єкт файлу (UploadFile).
            username (str): Ім'я користувача для формування public_id.

        Returns:
            str: URL завантаженого зображення з параметрами обрізки.
        """
        public_id = f"RestApp/{username}"
        result = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=result.get("version")
        )
        return src_url
