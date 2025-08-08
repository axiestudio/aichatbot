"""
Embed API - Secure iframe embedding and configuration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
from datetime import datetime, timedelta

from ....core.database import get_db
from ....models.database import ChatInstance, LiveConfiguration
from ....services.white_label_manager import white_label_manager
from ....services.tenant_manager import tenant_manager
from ....middleware.security_enhanced import SecurityEnhancementMiddleware

router = APIRouter(prefix="/embed", tags=["embed"])


@router.get("/{tenant_id}/config")
async def get_embed_config(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get configuration for embedded chat widget"""
    
    try:
        # Validate tenant exists and is active
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info or not tenant_info.get("is_active"):
            raise HTTPException(status_code=404, detail="Chat instance not found or inactive")
        
        # Get live configuration
        config = db.query(LiveConfiguration).filter(
            LiveConfiguration.instance_id == tenant_id,
            LiveConfiguration.is_active == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Get white-label branding
        branding = await white_label_manager.get_tenant_branding_config(tenant_id)
        
        # Build embed configuration
        embed_config = {
            "tenantId": tenant_id,
            "name": config.chat_title or branding["brandName"],
            "subtitle": config.chat_subtitle,
            "welcomeMessage": config.welcome_message,
            "placeholder": config.placeholder_text,
            "branding": branding,
            "features": {
                "typingIndicator": config.typing_indicator,
                "soundEnabled": config.sound_enabled,
                "autoScroll": config.auto_scroll,
                "messageTimestamps": config.message_timestamps,
                "fileUpload": config.file_upload_enabled,
                "maxFileSize": config.max_file_size_mb,
                "allowedFileTypes": config.allowed_file_types
            },
            "rateLimits": {
                "messagesPerMinute": config.messages_per_minute,
                "messagesPerHour": config.messages_per_hour
            },
            "conversationStarters": config.conversation_starters or [],
            "quickReplies": config.quick_replies or [],
            "customFields": config.custom_fields or {}
        }
        
        return embed_config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load configuration: {str(e)}")


@router.get("/{tenant_id}/css")
async def get_embed_css(
    tenant_id: str,
    request: Request
):
    """Get compiled CSS for embedded chat widget"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info or not tenant_info.get("is_active"):
            raise HTTPException(status_code=404, detail="Chat instance not found")
        
        # Get compiled CSS
        css = await white_label_manager.get_tenant_css(tenant_id)
        
        return Response(
            content=css,
            media_type="text/css",
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Type": "text/css"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load CSS: {str(e)}")


@router.get("/{tenant_id}/widget.js")
async def get_embed_widget_script(
    tenant_id: str,
    request: Request
):
    """Get JavaScript widget for embedding"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info or not tenant_info.get("is_active"):
            raise HTTPException(status_code=404, detail="Chat instance not found")
        
        # Get base URL
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # Generate widget JavaScript
        widget_js = f"""
(function() {{
    'use strict';
    
    // Widget configuration
    const TENANT_ID = '{tenant_id}';
    const BASE_URL = '{base_url}';
    const WIDGET_VERSION = '1.0.0';
    
    // Default configuration
    const defaultConfig = {{
        position: 'bottom-right',
        theme: 'auto',
        size: 'medium',
        showLauncher: true,
        launcherText: 'Chat with us',
        autoOpen: false,
        openDelay: 0,
        allowedDomains: [],
        customCSS: ''
    }};
    
    // Widget class
    class ChatWidget {{
        constructor(config = {{}}) {{
            this.config = {{ ...defaultConfig, ...config }};
            this.isLoaded = false;
            this.iframe = null;
            this.launcher = null;
            this.isOpen = false;
            
            this.init();
        }}
        
        async init() {{
            try {{
                // Load configuration from server
                const configResponse = await fetch(`${{BASE_URL}}/api/v1/embed/${{TENANT_ID}}/config`);
                if (!configResponse.ok) {{
                    throw new Error('Failed to load chat configuration');
                }}
                
                this.serverConfig = await configResponse.json();
                
                // Create widget elements
                this.createLauncher();
                this.createIframe();
                
                // Load CSS
                this.loadCSS();
                
                this.isLoaded = true;
                
                // Auto-open if configured
                if (this.config.autoOpen) {{
                    setTimeout(() => this.open(), this.config.openDelay);
                }}
                
            }} catch (error) {{
                console.error('Chat widget initialization failed:', error);
            }}
        }}
        
        createLauncher() {{
            if (!this.config.showLauncher) return;
            
            this.launcher = document.createElement('button');
            this.launcher.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            `;
            
            this.launcher.style.cssText = `
                position: fixed;
                ${{this.getPositionStyles()}}
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: ${{this.serverConfig?.branding?.primaryColor || '#3b82f6'}};
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 999999;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            
            this.launcher.addEventListener('click', () => this.toggle());
            this.launcher.addEventListener('mouseenter', () => {{
                this.launcher.style.transform = 'scale(1.1)';
            }});
            this.launcher.addEventListener('mouseleave', () => {{
                this.launcher.style.transform = 'scale(1)';
            }});
            
            document.body.appendChild(this.launcher);
        }}
        
        createIframe() {{
            this.iframe = document.createElement('iframe');
            this.iframe.src = `${{BASE_URL}}/chat/${{TENANT_ID}}?embedded=true`;
            this.iframe.style.cssText = `
                position: fixed;
                ${{this.getPositionStyles()}}
                ${{this.getSizeStyles()}}
                border: none;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
                z-index: 999998;
                display: none;
                background: white;
            `;
            
            this.iframe.allow = 'microphone; camera; geolocation';
            this.iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups');
            
            document.body.appendChild(this.iframe);
        }}
        
        loadCSS() {{
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = `${{BASE_URL}}/api/v1/embed/${{TENANT_ID}}/css`;
            document.head.appendChild(link);
        }}
        
        getPositionStyles() {{
            switch (this.config.position) {{
                case 'bottom-right':
                    return 'bottom: 20px; right: 20px;';
                case 'bottom-left':
                    return 'bottom: 20px; left: 20px;';
                case 'top-right':
                    return 'top: 20px; right: 20px;';
                case 'top-left':
                    return 'top: 20px; left: 20px;';
                default:
                    return 'bottom: 20px; right: 20px;';
            }}
        }}
        
        getSizeStyles() {{
            switch (this.config.size) {{
                case 'small':
                    return 'width: 320px; height: 400px;';
                case 'medium':
                    return 'width: 400px; height: 500px;';
                case 'large':
                    return 'width: 500px; height: 600px;';
                case 'fullscreen':
                    return 'width: 100vw; height: 100vh; top: 0; left: 0; border-radius: 0;';
                default:
                    return 'width: 400px; height: 500px;';
            }}
        }}
        
        open() {{
            if (!this.isLoaded || this.isOpen) return;
            
            this.iframe.style.display = 'block';
            this.isOpen = true;
            
            if (this.launcher) {{
                this.launcher.style.display = 'none';
            }}
        }}
        
        close() {{
            if (!this.isOpen) return;
            
            this.iframe.style.display = 'none';
            this.isOpen = false;
            
            if (this.launcher) {{
                this.launcher.style.display = 'flex';
            }}
        }}
        
        toggle() {{
            if (this.isOpen) {{
                this.close();
            }} else {{
                this.open();
            }}
        }}
        
        destroy() {{
            if (this.iframe) {{
                this.iframe.remove();
            }}
            if (this.launcher) {{
                this.launcher.remove();
            }}
        }}
    }}
    
    // Global API
    window.ChatWidget = ChatWidget;
    
    // Auto-initialize if config is provided
    if (window.chatWidgetConfig) {{
        window.chatWidget = new ChatWidget(window.chatWidgetConfig);
    }}
    
    // Expose initialization function
    window.initChatWidget = function(config) {{
        if (window.chatWidget) {{
            window.chatWidget.destroy();
        }}
        window.chatWidget = new ChatWidget(config);
        return window.chatWidget;
    }};
    
}})();
"""
        
        return Response(
            content=widget_js,
            media_type="application/javascript",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Type": "application/javascript"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate widget: {str(e)}")


@router.get("/{tenant_id}/embed-code")
async def get_embed_code(
    tenant_id: str,
    request: Request,
    config: Optional[str] = None
):
    """Get HTML embed code for the chat widget"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info or not tenant_info.get("is_active"):
            raise HTTPException(status_code=404, detail="Chat instance not found")
        
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        # Parse configuration if provided
        widget_config = "{}"
        if config:
            try:
                # Validate JSON
                json.loads(config)
                widget_config = config
            except json.JSONDecodeError:
                widget_config = "{}"
        
        embed_code = f"""<!-- Chat Widget Embed Code -->
<script>
  window.chatWidgetConfig = {widget_config};
</script>
<script src="{base_url}/api/v1/embed/{tenant_id}/widget.js" async></script>
<!-- End Chat Widget -->"""
        
        return {
            "embedCode": embed_code,
            "instructions": {
                "step1": "Copy the embed code above",
                "step2": "Paste it before the closing </body> tag on your website",
                "step3": "The chat widget will automatically initialize",
                "customization": "Modify the chatWidgetConfig object to customize appearance and behavior"
            },
            "configuration": {
                "position": "bottom-right | bottom-left | top-right | top-left",
                "theme": "light | dark | auto",
                "size": "small | medium | large | fullscreen",
                "showLauncher": "true | false",
                "autoOpen": "true | false",
                "openDelay": "delay in milliseconds"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed code: {str(e)}")


@router.post("/{tenant_id}/track-usage")
async def track_embed_usage(
    tenant_id: str,
    usage_data: Dict[str, Any],
    request: Request
):
    """Track usage analytics for embedded widget"""
    
    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Chat instance not found")
        
        # Extract usage metrics
        event_type = usage_data.get("event", "unknown")
        domain = usage_data.get("domain", request.headers.get("origin", "unknown"))
        user_agent = request.headers.get("user-agent", "unknown")
        
        # TODO: Store usage analytics in database
        # For now, just log the usage
        print(f"Widget usage - Tenant: {tenant_id}, Event: {event_type}, Domain: {domain}")
        
        return {"success": True, "message": "Usage tracked"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")
