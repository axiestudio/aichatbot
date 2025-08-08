"""
Advanced White-Label Manager - Comprehensive branding and customization system
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from ..core.database import get_db
from ..models.database import ChatInstance, LiveConfiguration
from ..services.cache_service import cache_service

logger = logging.getLogger(__name__)


class ThemeConfiguration(BaseModel):
    """Complete theme configuration for white-labeling"""
    
    # Brand Identity
    brand_name: str
    brand_logo_url: Optional[str] = None
    brand_favicon_url: Optional[str] = None
    brand_description: Optional[str] = None
    
    # Color Palette
    primary_color: str = "#3b82f6"
    secondary_color: str = "#e5e7eb"
    accent_color: str = "#10b981"
    background_color: str = "#ffffff"
    surface_color: str = "#f9fafb"
    text_primary: str = "#111827"
    text_secondary: str = "#6b7280"
    text_muted: str = "#9ca3af"
    border_color: str = "#e5e7eb"
    error_color: str = "#ef4444"
    warning_color: str = "#f59e0b"
    success_color: str = "#10b981"
    
    # Typography
    font_family_primary: str = "Inter, system-ui, sans-serif"
    font_family_secondary: str = "JetBrains Mono, monospace"
    font_size_base: str = "16px"
    font_weight_normal: str = "400"
    font_weight_medium: str = "500"
    font_weight_bold: str = "700"
    
    # Layout & Spacing
    border_radius: str = "8px"
    shadow_sm: str = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    shadow_md: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    shadow_lg: str = "0 10px 15px -3px rgb(0 0 0 / 0.1)"
    
    # Chat Interface Specific
    chat_bubble_user: str = "#3b82f6"
    chat_bubble_assistant: str = "#f3f4f6"
    chat_text_user: str = "#ffffff"
    chat_text_assistant: str = "#111827"
    chat_input_background: str = "#ffffff"
    chat_input_border: str = "#d1d5db"
    
    # Custom CSS
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    
    # Advanced Features
    show_powered_by: bool = True
    custom_footer_text: Optional[str] = None
    custom_header_html: Optional[str] = None
    
    @validator('primary_color', 'secondary_color', 'accent_color', 'background_color', 
              'surface_color', 'text_primary', 'text_secondary', 'text_muted', 
              'border_color', 'error_color', 'warning_color', 'success_color',
              'chat_bubble_user', 'chat_bubble_assistant', 'chat_text_user', 
              'chat_text_assistant', 'chat_input_background', 'chat_input_border')
    def validate_color(cls, v):
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v


class WhiteLabelManager:
    """
    Advanced white-label manager for comprehensive branding and customization
    """
    
    def __init__(self):
        self.theme_cache = {}
        self.css_cache = {}
        
    async def initialize(self):
        """Initialize white-label manager"""
        logger.info("🎨 Initializing Advanced White-Label Manager...")
        await self._load_all_themes()
        logger.info("✅ White-Label Manager initialized")
    
    async def _load_all_themes(self):
        """Load all tenant themes into cache"""
        try:
            db = next(get_db())
            configurations = db.query(LiveConfiguration).all()
            
            for config in configurations:
                theme = await self._build_theme_from_config(config)
                self.theme_cache[config.instance_id] = theme
                
                # Generate and cache CSS
                css = await self._generate_css_from_theme(theme)
                self.css_cache[config.instance_id] = css
                
            logger.info(f"Loaded {len(configurations)} theme configurations")
            
        except Exception as e:
            logger.error(f"Failed to load theme configurations: {e}")
    
    async def _build_theme_from_config(self, config: LiveConfiguration) -> ThemeConfiguration:
        """Build theme configuration from live configuration"""
        
        # Extract theme data from configuration
        theme_data = {
            "brand_name": config.company_name or config.chat_title,
            "brand_logo_url": config.logo_url,
            "primary_color": config.primary_color,
            "secondary_color": config.secondary_color,
            "accent_color": config.accent_color,
            "background_color": config.background_color,
            "text_primary": config.text_color,
            "custom_css": config.custom_css,
            "show_powered_by": config.show_branding,
        }
        
        # Fill in defaults for missing values
        return ThemeConfiguration(**{k: v for k, v in theme_data.items() if v is not None})
    
    async def get_tenant_theme(self, tenant_id: str) -> ThemeConfiguration:
        """Get theme configuration for tenant"""
        if tenant_id in self.theme_cache:
            return self.theme_cache[tenant_id]
        
        # Load from database if not cached
        try:
            db = next(get_db())
            config = db.query(LiveConfiguration).filter(
                LiveConfiguration.instance_id == tenant_id
            ).first()
            
            if config:
                theme = await self._build_theme_from_config(config)
                self.theme_cache[tenant_id] = theme
                return theme
            
        except Exception as e:
            logger.error(f"Error loading theme for tenant {tenant_id}: {e}")
        
        # Return default theme
        return ThemeConfiguration(brand_name="AI Assistant")
    
    async def update_tenant_theme(self, tenant_id: str, theme_updates: Dict[str, Any]) -> ThemeConfiguration:
        """Update tenant theme configuration"""
        try:
            # Get current theme
            current_theme = await self.get_tenant_theme(tenant_id)
            
            # Apply updates
            theme_dict = current_theme.dict()
            theme_dict.update(theme_updates)
            
            # Validate new theme
            updated_theme = ThemeConfiguration(**theme_dict)
            
            # Update database
            db = next(get_db())
            config = db.query(LiveConfiguration).filter(
                LiveConfiguration.instance_id == tenant_id
            ).first()
            
            if config:
                # Update relevant fields
                config.company_name = updated_theme.brand_name
                config.logo_url = updated_theme.brand_logo_url
                config.primary_color = updated_theme.primary_color
                config.secondary_color = updated_theme.secondary_color
                config.accent_color = updated_theme.accent_color
                config.background_color = updated_theme.background_color
                config.text_color = updated_theme.text_primary
                config.custom_css = updated_theme.custom_css
                config.show_branding = updated_theme.show_powered_by
                config.updated_at = datetime.utcnow()
                
                db.commit()
            
            # Update cache
            self.theme_cache[tenant_id] = updated_theme
            
            # Regenerate CSS
            css = await self._generate_css_from_theme(updated_theme)
            self.css_cache[tenant_id] = css
            
            return updated_theme
            
        except Exception as e:
            logger.error(f"Error updating theme for tenant {tenant_id}: {e}")
            raise
    
    async def _generate_css_from_theme(self, theme: ThemeConfiguration) -> str:
        """Generate CSS from theme configuration"""
        
        css_template = f"""
/* Auto-generated theme CSS for {theme.brand_name} */
:root {{
  /* Brand Colors */
  --brand-primary: {theme.primary_color};
  --brand-secondary: {theme.secondary_color};
  --brand-accent: {theme.accent_color};
  --brand-background: {theme.background_color};
  --brand-surface: {theme.surface_color};
  
  /* Text Colors */
  --text-primary: {theme.text_primary};
  --text-secondary: {theme.text_secondary};
  --text-muted: {theme.text_muted};
  
  /* Status Colors */
  --color-error: {theme.error_color};
  --color-warning: {theme.warning_color};
  --color-success: {theme.success_color};
  
  /* Typography */
  --font-family-primary: {theme.font_family_primary};
  --font-family-secondary: {theme.font_family_secondary};
  --font-size-base: {theme.font_size_base};
  --font-weight-normal: {theme.font_weight_normal};
  --font-weight-medium: {theme.font_weight_medium};
  --font-weight-bold: {theme.font_weight_bold};
  
  /* Layout */
  --border-radius: {theme.border_radius};
  --border-color: {theme.border_color};
  --shadow-sm: {theme.shadow_sm};
  --shadow-md: {theme.shadow_md};
  --shadow-lg: {theme.shadow_lg};
  
  /* Chat Interface */
  --chat-bubble-user: {theme.chat_bubble_user};
  --chat-bubble-assistant: {theme.chat_bubble_assistant};
  --chat-text-user: {theme.chat_text_user};
  --chat-text-assistant: {theme.chat_text_assistant};
  --chat-input-bg: {theme.chat_input_background};
  --chat-input-border: {theme.chat_input_border};
}}

/* Base Styles */
.chat-interface {{
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  color: var(--text-primary);
  background-color: var(--brand-background);
}}

/* Chat Messages */
.message-user {{
  background-color: var(--chat-bubble-user);
  color: var(--chat-text-user);
  border-radius: var(--border-radius);
}}

.message-assistant {{
  background-color: var(--chat-bubble-assistant);
  color: var(--chat-text-assistant);
  border-radius: var(--border-radius);
}}

/* Input Area */
.chat-input {{
  background-color: var(--chat-input-bg);
  border: 1px solid var(--chat-input-border);
  border-radius: var(--border-radius);
  color: var(--text-primary);
}}

.chat-input:focus {{
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}}

/* Buttons */
.btn-primary {{
  background-color: var(--brand-primary);
  color: white;
  border-radius: var(--border-radius);
  font-weight: var(--font-weight-medium);
}}

.btn-primary:hover {{
  background-color: color-mix(in srgb, var(--brand-primary) 90%, black);
}}

/* Header */
.chat-header {{
  background-color: var(--brand-surface);
  border-bottom: 1px solid var(--border-color);
}}

/* Branding */
.brand-logo {{
  max-height: 32px;
  width: auto;
}}

.powered-by {{
  display: {'' if theme.show_powered_by else 'none'};
  font-size: 0.75rem;
  color: var(--text-muted);
}}

/* Custom CSS */
{theme.custom_css or ''}
"""
        
        return css_template.strip()
    
    async def get_tenant_css(self, tenant_id: str) -> str:
        """Get compiled CSS for tenant"""
        if tenant_id in self.css_cache:
            return self.css_cache[tenant_id]
        
        # Generate CSS if not cached
        theme = await self.get_tenant_theme(tenant_id)
        css = await self._generate_css_from_theme(theme)
        self.css_cache[tenant_id] = css
        
        return css
    
    async def get_tenant_branding_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get branding configuration for frontend"""
        theme = await self.get_tenant_theme(tenant_id)
        
        return {
            "brandName": theme.brand_name,
            "logoUrl": theme.brand_logo_url,
            "faviconUrl": theme.brand_favicon_url,
            "description": theme.brand_description,
            "primaryColor": theme.primary_color,
            "secondaryColor": theme.secondary_color,
            "accentColor": theme.accent_color,
            "showPoweredBy": theme.show_powered_by,
            "customFooterText": theme.custom_footer_text,
            "customHeaderHtml": theme.custom_header_html,
        }
    
    async def validate_custom_css(self, css: str) -> Dict[str, Any]:
        """Validate custom CSS for security and syntax"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check for potentially dangerous CSS
        dangerous_patterns = [
            r'@import\s+url\s*\(',  # External imports
            r'expression\s*\(',     # IE expressions
            r'javascript:',         # JavaScript URLs
            r'vbscript:',          # VBScript URLs
            r'data:.*base64',      # Base64 data URLs
            r'@media\s+print',     # Print media (could hide content)
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, css, re.IGNORECASE):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Potentially dangerous CSS pattern detected: {pattern}")
        
        # Check CSS size limit (100KB)
        if len(css.encode('utf-8')) > 100 * 1024:
            validation_result["valid"] = False
            validation_result["errors"].append("CSS exceeds maximum size limit (100KB)")
        
        # Basic CSS syntax validation (simplified)
        brace_count = css.count('{') - css.count('}')
        if brace_count != 0:
            validation_result["warnings"].append("Unmatched braces detected in CSS")
        
        return validation_result
    
    async def clear_tenant_cache(self, tenant_id: str):
        """Clear cached data for tenant"""
        self.theme_cache.pop(tenant_id, None)
        self.css_cache.pop(tenant_id, None)


# Global white-label manager instance
white_label_manager = WhiteLabelManager()
