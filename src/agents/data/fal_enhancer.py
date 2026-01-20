"""
FAL.AI Enhancer
Uses Flux Kontext Pro via FAL.AI API to professionalize product images.
"""
import os
import requests
import fal_client
import base64
import io
from typing import Optional, Dict, Any
from PIL import Image, ImageChops, ImageOps

class FalEnhancer:
    """
    Enhances images using Fal.ai Flux Kontext Pro.
    """
    
    API_URL = "https://fal.run/fal-ai/flux-pro/kontext"
    
    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")
        if not self.api_key:
            # Try loading from .env
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.getenv("FAL_KEY")
            except:
                pass
                
    def enhance_image(self, image_path: str, product_context: Dict[str, Any]) -> Optional[str]:
        """
        Enhance an image using FAL.AI.
        Returns: Path to the enhanced image (saved locally in data/processed_images) or None.
        """
        if not self.api_key:
            print("⚠️ FAL_KEY not found in environment.")
            return None
            
        if not os.path.exists(image_path):
            print(f"⚠️ Image not found: {image_path}")
            return None

        # 1. Prepare Prompt (Dynamic/Abstract as requested)
        brand = product_context.get('brand', 'Premium Brand')
        p_type = product_context.get('type', 'Industrial Component')
        
        # Abstract prompt structure that adapts to the product
        prompt = f"""
        Ultra premium product photography of a {brand} {p_type}. 
        Style: Swiss Minimalist Design, High-End Industrial Catalog.
        Background: Pure #FFFFFF White Background.
        Lighting: Soft, diffused studio lighting, no harsh glare.
        Shadows: Realistic soft contact shadow to ground the object.
        Details: Razor unique metallic texture, 8k resolution, photorealistic, pristine condition.
        Keep the object geometry exactly 100% original.
        NO TEXT, NO LABELS, NO WATERMARKS, NO ENGRAVINGS on the background or surrounding.
        """
        
        try:
            # 2. Encode Image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            image_url = f"data:image/jpeg;base64,{image_data}"
            
            # 3. Call API
            headers = {
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": prompt.strip(),
                "image_url": image_url,
                "guidance_scale": 7.5,
                "num_inference_steps": 25,
                "seed": 42 
            }
            
            print(f"   🎨 Sending to FAL.AI ({p_type})...")
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if "images" in result and result["images"]:
                    return self._process_result(result["images"][0]["url"], image_path)
            else:
                 print(f"❌ FAL API Error: {response.status_code} - {response.text}")
                 
        except Exception as e:
            print(f"❌ FAL Exception: {e}")
            return None
            
        return None

    def _process_result(self, url: str, original_path: str) -> str:
        """Download, Trim, and Standardize Result"""
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content))
                
                # 1. Trim Whitespace (Fuzzy Smart Crop)
                # Convert to grayscale to find non-white content (ignoring near-white noise)
                gray = img.convert("L")
                # Invert so content is white, background is black
                gray = ImageOps.invert(gray)
                # Threshold: Treat anything brighter than 250 (near white) as black (background)
                # This removes light shadows/vignettes from the crop calculation
                threshold = 245
                mask = gray.point(lambda p: 255 if p > (255 - threshold) else 0)
                
                bbox = mask.getbbox()
                if bbox:
                    img = img.crop(bbox)
                
                # Odoo Standardization: 1024x1024 w/ white canvas
                canvas = Image.new('RGB', (1024, 1024), (255, 255, 255))
                
                # 2. Resize to Fill (Tight Fit)
                # Target: Fill 98% of canvas (approx 1000px) to minimize whitespace per user request
                target_size = 1000
                
                # Calculate resize ratio maintaining aspect ratio
                width_ratio = target_size / img.width
                height_ratio = target_size / img.height
                scale = min(width_ratio, height_ratio)
                
                new_width = int(img.width * scale)
                new_height = int(img.height * scale)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center
                x = (1024 - new_width) // 2
                y = (1024 - new_height) // 2
                canvas.paste(img, (x, y))
                
                # Save
                dirname = os.path.dirname(original_path)
                filename = os.path.basename(original_path)
                name, ext = os.path.splitext(filename)
                
                # Save in a 'processed' subfolder to avoid overwriting or mixing
                output_dir = os.path.join(dirname, "processed")
                os.makedirs(output_dir, exist_ok=True)
                
                # User requested '_swiss' tag
                output_path = os.path.join(output_dir, f"{name}_swiss.jpg")
                canvas.save(output_path, "JPEG", quality=95)
                
                return output_path
        except Exception as e:
            print(f"Error processing result image: {e}")
            return None

    def generate_from_text(self, prompt: str, filename: str) -> str:
        """
        Generate a new image from scratch (Text-to-Image) for generic categories.
        """
        print(f"   🎨 Generating Generic: {filename}...")
        
        try:
            # Ensure env var is set for the library
            if self.api_key:
                os.environ["FAL_KEY"] = self.api_key
                
            handler = fal_client.submit(
                "fal-ai/flux-pro/v1.1-ultra",
                arguments={
                    "prompt": prompt + " Style: Swiss Minimalist Design, High-End Industrial Catalog. Background: Pure #FFFFFF White Background. Lighting: Soft, diffused studio lighting. Shadows: Realistic soft contact shadow. NO TEXT, NO LABELS.",
                    "image_size": "square_hd",
                    "safety_tolerance": "2",
                },
            )
            result = handler.get()
            
            if result and 'images' in result and len(result['images']) > 0:
                image_url = result['images'][0]['url']
                
                # Use same post-processing (Trim + Resize)
                # Create a dummy path to reuse logic
                assets_dir = os.path.join(os.getcwd(), "projects", "odoo-bearings-config", "data", "assets", "product_images", "generics")
                os.makedirs(assets_dir, exist_ok=True)
                dummy_path = os.path.join(assets_dir, filename)
                
                return self._process_result(image_url, dummy_path)
                
        except Exception as e:
            print(f"Error generating generic: {e}")
            return None
