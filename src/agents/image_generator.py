"""
ImageGeneratorAgent - Professional Image Generation for Odoo Websites

Generates high-quality, cinematic images for eCommerce websites
Inspired by Christopher Nolan's visual style: dramatic, professional, impactful
"""
from typing import Any, Dict, List

from .base import OdooAgent


class ImageGeneratorAgent(OdooAgent):
    """Agent for generating professional website images"""
    
    def __init__(self, odoo_connector):
        super().__init__(odoo_connector)
        self.name = "ImageGeneratorAgent"
        self.description = "Generates professional, cinematic images for websites"
        
        # Christopher Nolan style characteristics
        self.style_guide = {
            'aesthetic': 'cinematic, dramatic, professional',
            'lighting': 'high contrast, dramatic shadows, golden hour',
            'composition': 'rule of thirds, leading lines, depth',
            'color_palette': 'desaturated with accent colors, teal and orange',
            'mood': 'serious, impactful, premium',
            'quality': 'ultra high resolution, sharp focus, detailed'
        }
    
    def can_handle(self, request: str) -> bool:
        """Check if agent can handle the request"""
        keywords = [
            'image', 'generate', 'create image', 'banner', 'hero',
            'logo', 'icon', 'visual', 'graphic', 'photo'
        ]
        return any(keyword in request.lower() for keyword in keywords)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute image generation"""
        self.log("Starting image generation")
        
        image_type = params.get('type', 'hero')
        subject = params.get('subject', 'industrial machinery')
        style = params.get('style', 'professional')
        
        if image_type == 'hero':
            return self._generate_hero_banner(params)
        elif image_type == 'category':
            return self._generate_category_images(params)
        elif image_type == 'logo':
            return self._generate_logo(params)
        elif image_type == 'icons':
            return self._generate_feature_icons(params)
        elif image_type == 'all':
            return self._generate_complete_set(params)
        else:
            return {'status': 'error', 'message': f'Unknown image type: {image_type}'}
    
    def _generate_hero_banner(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate hero banner with Christopher Nolan aesthetic"""
        company = params.get('company', 'Company')
        industry = params.get('industry', 'industrial')
        
        prompt = f"""
        Cinematic hero banner for {company} website, {industry} industry.
        
        Style: Christopher Nolan cinematography
        - Ultra wide angle shot (2.39:1 aspect ratio)
        - Dramatic high contrast lighting with deep shadows
        - Teal and orange color grading
        - Golden hour lighting
        - Sharp focus on industrial machinery in foreground
        - Blurred background with depth of field
        - Professional, serious, impactful mood
        - Premium quality, ultra detailed
        - No text, clean composition
        - Rule of thirds composition
        
        Scene: Industrial facility at sunset, precision machinery in dramatic lighting,
        professional workers in background (blurred), sense of scale and precision,
        cinematic atmosphere, IMAX quality
        """
        
        return {
            'status': 'success',
            'type': 'hero_banner',
            'prompt': prompt.strip(),
            'filename': f'{company.lower()}_hero_banner.png',
            'dimensions': '2400x1000'
        }
    
    def _generate_category_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate category images"""
        categories = params.get('categories', [])
        results = []
        
        base_style = """
        Christopher Nolan cinematography style:
        - Dramatic lighting, high contrast
        - Teal and orange color palette
        - Sharp macro focus
        - Professional studio lighting
        - Dark background with rim lighting
        - Ultra detailed, premium quality
        - Serious, impactful mood
        """
        
        category_prompts = {
            'Ball Bearings': f"""
            Extreme macro shot of precision ball bearings.
            {base_style}
            Composition: Single ball bearing in sharp focus, others blurred in background,
            metallic reflections, precision engineering visible, dramatic side lighting
            """,
            
            'Roller Bearings': f"""
            Cinematic shot of industrial roller bearings.
            {base_style}
            Composition: Roller bearing assembly, dramatic angle, industrial setting,
            precision components visible, professional lighting setup
            """,
            
            'Thrust Bearings': f"""
            Professional studio shot of thrust bearing mechanism.
            {base_style}
            Composition: Thrust bearing in dramatic lighting, technical precision visible,
            dark background, golden rim light, engineering excellence
            """,
            
            'Special Bearings': f"""
            Artistic shot of specialized precision bearings.
            {base_style}
            Composition: Unique bearing design, dramatic presentation, high-tech feel,
            precision engineering, premium quality visible
            """
        }
        
        for category in categories:
            if category in category_prompts:
                results.append({
                    'category': category,
                    'prompt': category_prompts[category].strip(),
                    'filename': f'{category.lower().replace(" ", "_")}.png',
                    'dimensions': '800x600'
                })
        
        return {
            'status': 'success',
            'type': 'category_images',
            'images': results,
            'count': len(results)
        }
    
    def _generate_logo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional logo"""
        company = params.get('company', 'Company')
        
        prompt = f"""
        Professional minimalist logo for {company}.
        
        Style: Modern, clean, premium
        - Geometric design
        - Industrial aesthetic
        - Monochrome or subtle color
        - Scalable vector style
        - Professional typography
        - Memorable and impactful
        - Works on dark and light backgrounds
        
        Design: Abstract bearing/gear element combined with clean typography,
        precision engineering feel, trustworthy and established brand
        """
        
        return {
            'status': 'success',
            'type': 'logo',
            'prompt': prompt.strip(),
            'filename': f'{company.lower()}_logo.png',
            'dimensions': '1000x1000'
        }
    
    def _generate_feature_icons(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate feature icons"""
        features = params.get('features', [
            'Fast Shipping',
            'Quality Guarantee',
            '24/7 Support',
            'Premium Quality'
        ])
        
        results = []
        
        for feature in features:
            prompt = f"""
            Professional icon for '{feature}' feature.
            
            Style: Minimalist, modern, clean
            - Simple geometric shapes
            - Monochrome or single accent color
            - Clear and recognizable
            - Professional and trustworthy
            - Scalable design
            
            Icon should clearly represent {feature} in a professional industrial context
            """
            
            results.append({
                'feature': feature,
                'prompt': prompt.strip(),
                'filename': f'icon_{feature.lower().replace(" ", "_")}.png',
                'dimensions': '200x200'
            })
        
        return {
            'status': 'success',
            'type': 'feature_icons',
            'icons': results,
            'count': len(results)
        }
    
    def _generate_complete_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete image set for website"""
        results = {
            'hero': self._generate_hero_banner(params),
            'categories': self._generate_category_images(params),
            'logo': self._generate_logo(params),
            'icons': self._generate_feature_icons(params)
        }
        
        total_images = (
            1 +  # hero
            len(results['categories'].get('images', [])) +
            1 +  # logo
            len(results['icons'].get('icons', []))
        )
        
        return {
            'status': 'success',
            'type': 'complete_set',
            'results': results,
            'total_images': total_images
        }
