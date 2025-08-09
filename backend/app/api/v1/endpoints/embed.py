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
from ....services.subscription_manager import subscription_manager
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

        # Get subscription and branding permissions
        branding_permissions = await subscription_manager.check_branding_permissions(tenant_id, db)

        # Build embed configuration
        embed_config = {
            "tenantId": tenant_id,
            "name": config.chat_title or branding["brandName"],
            "subtitle": config.chat_subtitle,
            "welcomeMessage": config.welcome_message,
            "placeholder": config.placeholder_text,
            "branding": branding,
            "subscription": {
                "tier": branding_permissions["tier"],
                "canRemoveBranding": branding_permissions["can_remove_branding"],
                "canCustomBrand": branding_permissions["can_custom_brand"],
                "canWhiteLabel": branding_permissions["can_white_label"],
                "isTrial": branding_permissions["is_trial"],
                "trialDaysLeft": branding_permissions["trial_days_left"],
                "usagePercentage": branding_permissions["usage_percentage"],
                "usageExceeded": branding_permissions["usage_exceeded"]
            },
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
        
        # Generate widget JavaScript with Axie Studio branding
        widget_js = f"""
(function() {{
    'use strict';

    // Axie Studio Chat Widget Configuration
    const TENANT_ID = '{tenant_id}';
    const BASE_URL = '{base_url}';
    const WIDGET_VERSION = '2.0.0';
    const POWERED_BY = 'Axie Studio';
    const POWERED_BY_URL = 'https://axiestudio.se';

    // Default configuration with Axie Studio branding
    const defaultConfig = {{
        position: 'bottom-right',
        theme: 'auto',
        size: 'medium',
        showLauncher: true,
        launcherText: 'Chat with us',
        autoOpen: false,
        openDelay: 0,
        allowedDomains: [],
        customCSS: '',
        showPoweredBy: true,
        customColors: {{
            primary: '#8B5CF6',
            secondary: '#EC4899',
            background: '#FFFFFF',
            text: '#1F2937'
        }},
        animation: 'slide',
        closeOnOutsideClick: true
    }};

    // Axie Studio Chat Widget Class
    class AxieChatWidget {{
        constructor(config = {{}}) {{
            this.config = {{ ...defaultConfig, ...config }};
            this.isLoaded = false;
            this.iframe = null;
            this.launcher = null;
            this.isOpen = false;
            this.serverConfig = null;

            // Validate domain if restrictions are set
            if (this.config.allowedDomains.length > 0) {{
                const currentDomain = window.location.hostname;
                const isAllowed = this.config.allowedDomains.some(domain => {{
                    if (domain.startsWith('*.')) {{
                        const baseDomain = domain.substring(2);
                        return currentDomain.endsWith(baseDomain);
                    }}
                    return currentDomain === domain;
                }});

                if (!isAllowed) {{
                    console.warn('Axie Studio Chat Widget: Domain not allowed');
                    return;
                }}
            }}

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

                // Merge server config with client config
                this.config = {{
                    ...this.config,
                    ...this.serverConfig.branding,
                    customColors: {{
                        ...this.config.customColors,
                        ...this.serverConfig.branding?.colors
                    }}
                }};

                // Create widget elements
                this.createLauncher();
                this.createIframe();

                // Load CSS
                this.loadCSS();

                // Track widget load
                this.trackUsage('widget_loaded');

                this.isLoaded = true;

                // Auto-open if configured
                if (this.config.autoOpen) {{
                    setTimeout(() => this.open(), this.config.openDelay);
                }}

            }} catch (error) {{
                console.error('Axie Studio Chat Widget initialization failed:', error);
                this.showErrorState();
            }}
        }}
        
        createLauncher() {{
            if (!this.config.showLauncher) return;

            this.launcher = document.createElement('button');
            this.launcher.setAttribute('aria-label', 'Open Axie Studio Chat');
            this.launcher.setAttribute('title', this.config.launcherText || 'Chat with us');

            // Enhanced launcher with Axie Studio branding
            this.launcher.innerHTML = `
                <div class="axie-launcher-content">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        <path d="M8 10h.01M12 10h.01M16 10h.01"></path>
                    </svg>
                    <div class="axie-launcher-pulse"></div>
                </div>
            `;

            const primaryColor = this.config.customColors?.primary || '#8B5CF6';
            const secondaryColor = this.config.customColors?.secondary || '#EC4899';

            this.launcher.style.cssText = `
                position: fixed;
                ${{this.getPositionStyles()}}
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background: linear-gradient(135deg, ${{primaryColor}}, ${{secondaryColor}});
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3);
                z-index: 999999;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                overflow: hidden;
            `;

            // Add CSS for pulse animation
            const style = document.createElement('style');
            style.textContent = `
                .axie-launcher-content {{
                    position: relative;
                    z-index: 2;
                }}
                .axie-launcher-pulse {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                    animation: axie-pulse 2s infinite;
                }}
                @keyframes axie-pulse {{
                    0% {{ transform: scale(1); opacity: 1; }}
                    100% {{ transform: scale(1.4); opacity: 0; }}
                }}
                .axie-launcher-tooltip {{
                    position: absolute;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 14px;
                    white-space: nowrap;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                    pointer-events: none;
                    z-index: 1000000;
                }}
            `;
            document.head.appendChild(style);

            // Add tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'axie-launcher-tooltip';
            tooltip.textContent = this.config.launcherText || 'Chat with us';
            tooltip.style.cssText = this.getTooltipPosition();
            this.launcher.appendChild(tooltip);

            // Event listeners with enhanced interactions
            this.launcher.addEventListener('click', () => {{
                this.toggle();
                this.trackUsage('launcher_clicked');
            }});

            this.launcher.addEventListener('mouseenter', () => {{
                this.launcher.style.transform = 'scale(1.1)';
                this.launcher.style.boxShadow = '0 12px 40px rgba(139, 92, 246, 0.4)';
                tooltip.style.opacity = '1';
            }});

            this.launcher.addEventListener('mouseleave', () => {{
                this.launcher.style.transform = 'scale(1)';
                this.launcher.style.boxShadow = '0 8px 32px rgba(139, 92, 246, 0.3)';
                tooltip.style.opacity = '0';
            }});

            document.body.appendChild(this.launcher);
        }}
        
        createIframe() {{
            // Create iframe container with Axie Studio branding
            this.iframeContainer = document.createElement('div');
            this.iframeContainer.className = 'axie-chat-container';

            // Create header with branding
            const header = document.createElement('div');
            header.className = 'axie-chat-header';
            header.innerHTML = `
                <div class="axie-chat-header-content">
                    <div class="axie-chat-brand">
                        <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" class="axie-brand-logo" />
                        <div class="axie-brand-text">
                            <div class="axie-brand-name">${{this.serverConfig?.name || 'AI Assistant'}}</div>
                            ${{this.shouldShowBranding() ? '<div class="axie-brand-subtitle">Powered by Axie Studio</div>' : ''}}
                        </div>
                    </div>
                    <button class="axie-chat-close" aria-label="Close chat">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            `;

            // Create iframe
            this.iframe = document.createElement('iframe');
            this.iframe.src = `${{BASE_URL}}/chat/${{TENANT_ID}}?embedded=true&theme=${{this.config.theme}}`;
            this.iframe.className = 'axie-chat-iframe';

            // Assemble container
            this.iframeContainer.appendChild(header);
            this.iframeContainer.appendChild(this.iframe);

            const primaryColor = this.config.customColors?.primary || '#8B5CF6';
            const secondaryColor = this.config.customColors?.secondary || '#EC4899';

            // Enhanced styling with Axie Studio branding
            this.iframeContainer.style.cssText = `
                position: fixed;
                ${{this.getPositionStyles()}}
                ${{this.getSizeStyles()}}
                border: none;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                z-index: 999998;
                display: none;
                background: white;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                transform: translateY(20px);
                opacity: 0;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            `;

            // Header styling
            header.style.cssText = `
                background: linear-gradient(135deg, ${{primaryColor}}, ${{secondaryColor}});
                color: white;
                padding: 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-radius: 16px 16px 0 0;
            `;

            // Iframe styling
            this.iframe.style.cssText = `
                width: 100%;
                height: calc(100% - 72px);
                border: none;
                background: white;
            `;

            this.iframe.allow = 'microphone; camera; geolocation';
            this.iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox');

            // Add header styles
            const headerStyle = document.createElement('style');
            headerStyle.textContent = `
                .axie-chat-header-content {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    width: 100%;
                }}
                .axie-chat-brand {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                .axie-brand-logo {{
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    object-fit: cover;
                }}
                .axie-brand-text {{
                    display: flex;
                    flex-direction: column;
                }}
                .axie-brand-name {{
                    font-weight: 600;
                    font-size: 16px;
                    line-height: 1.2;
                }}
                .axie-brand-subtitle {{
                    font-size: 12px;
                    opacity: 0.9;
                    line-height: 1.2;
                }}
                .axie-chat-close {{
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s ease;
                }}
                .axie-chat-close:hover {{
                    background: rgba(255, 255, 255, 0.3);
                }}
            `;
            document.head.appendChild(headerStyle);

            // Close button functionality
            const closeButton = header.querySelector('.axie-chat-close');
            closeButton.addEventListener('click', () => {{
                this.close();
                this.trackUsage('chat_closed');
            }});

            // Outside click to close
            if (this.config.closeOnOutsideClick) {{
                document.addEventListener('click', (e) => {{
                    if (this.isOpen && !this.iframeContainer.contains(e.target) && !this.launcher.contains(e.target)) {{
                        this.close();
                    }}
                }});
            }}

            document.body.appendChild(this.iframeContainer);
        }}
        
        loadCSS() {{
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = `${{BASE_URL}}/api/v1/embed/${{TENANT_ID}}/css`;
            document.head.appendChild(link);
        }}

        getTooltipPosition() {{
            switch (this.config.position) {{
                case 'bottom-right':
                    return 'bottom: 80px; right: 0px;';
                case 'bottom-left':
                    return 'bottom: 80px; left: 0px;';
                case 'top-right':
                    return 'top: 80px; right: 0px;';
                case 'top-left':
                    return 'top: 80px; left: 0px;';
                default:
                    return 'bottom: 80px; right: 0px;';
            }}
        }}

        showErrorState() {{
            if (this.launcher) {{
                this.launcher.style.background = '#EF4444';
                this.launcher.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                `;
                this.launcher.title = 'Chat widget failed to load';
            }}
        }}

        shouldShowBranding() {{
            // Always show branding for free tier
            if (!this.serverConfig?.subscription) {{
                return true;
            }}

            const subscription = this.serverConfig.subscription;

            // Hide branding if user can remove it (premium/enterprise)
            if (subscription.canRemoveBranding && !subscription.isTrial) {{
                return false;
            }}

            // Show branding during trial
            if (subscription.isTrial) {{
                return true;
            }}

            // Default: show branding
            return true;
        }}

        trackUsage(event) {{
            try {{
                fetch(`${{BASE_URL}}/api/v1/embed/${{TENANT_ID}}/track-usage`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        event: event,
                        domain: window.location.hostname,
                        timestamp: new Date().toISOString(),
                        userAgent: navigator.userAgent,
                        config: this.config,
                        subscription: this.serverConfig?.subscription
                    }})
                }});
            }} catch (error) {{
                console.warn('Failed to track usage:', error);
            }}
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

            this.iframeContainer.style.display = 'block';

            // Animate in
            requestAnimationFrame(() => {{
                this.iframeContainer.style.opacity = '1';
                this.iframeContainer.style.transform = 'translateY(0)';
            }});

            this.isOpen = true;

            if (this.launcher) {{
                this.launcher.style.opacity = '0';
                this.launcher.style.transform = 'scale(0.8)';
                setTimeout(() => {{
                    this.launcher.style.display = 'none';
                }}, 150);
            }}

            this.trackUsage('chat_opened');
        }}

        close() {{
            if (!this.isOpen) return;

            // Animate out
            this.iframeContainer.style.opacity = '0';
            this.iframeContainer.style.transform = 'translateY(20px)';

            setTimeout(() => {{
                this.iframeContainer.style.display = 'none';
            }}, 300);

            this.isOpen = false;

            if (this.launcher) {{
                this.launcher.style.display = 'flex';
                requestAnimationFrame(() => {{
                    this.launcher.style.opacity = '1';
                    this.launcher.style.transform = 'scale(1)';
                }});
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
            if (this.iframeContainer) {{
                this.iframeContainer.remove();
            }}
            if (this.launcher) {{
                this.launcher.remove();
            }}
            this.trackUsage('widget_destroyed');
        }}
    }}

    // Global Axie Studio Chat Widget API
    window.AxieChatWidget = AxieChatWidget;
    window.ChatWidget = AxieChatWidget; // Backward compatibility

    // Auto-initialize if config is provided
    if (window.chatWidgetConfig) {{
        window.axieChatWidget = new AxieChatWidget(window.chatWidgetConfig);
        window.chatWidget = window.axieChatWidget; // Backward compatibility
    }}

    // Expose initialization function
    window.initAxieChatWidget = function(config) {{
        if (window.axieChatWidget) {{
            window.axieChatWidget.destroy();
        }}
        window.axieChatWidget = new AxieChatWidget(config);
        window.chatWidget = window.axieChatWidget; // Backward compatibility
        return window.axieChatWidget;
    }};

    // Backward compatibility
    window.initChatWidget = window.initAxieChatWidget;

    // Console branding
    console.log('%c🎨 Axie Studio Chat Widget v2.0.0', 'color: #8B5CF6; font-weight: bold; font-size: 14px;');
    console.log('%c🚀 Powered by Axie Studio - https://axiestudio.se', 'color: #EC4899; font-size: 12px;');
    
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


@router.post("/{tenant_id}/customize")
async def customize_embed_widget(
    tenant_id: str,
    customization: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """Update embed widget customization settings"""

    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Chat instance not found")

        # Update white-label branding with new customization
        branding_update = {
            "colors": customization.get("customColors", {}),
            "position": customization.get("position", "bottom-right"),
            "theme": customization.get("theme", "auto"),
            "size": customization.get("size", "medium"),
            "showLauncher": customization.get("showLauncher", True),
            "autoOpen": customization.get("autoOpen", False),
            "launcherText": customization.get("launcherText", "Chat with us"),
            "allowedDomains": customization.get("allowedDomains", "").split('\n') if customization.get("allowedDomains") else [],
            "showPoweredBy": customization.get("showPoweredBy", True),
            "animation": customization.get("animation", "slide"),
            "closeOnOutsideClick": customization.get("closeOnOutsideClick", True)
        }

        # Save to white-label manager
        await white_label_manager.update_tenant_branding(tenant_id, branding_update)

        return {
            "success": True,
            "message": "Widget customization updated successfully",
            "branding": branding_update
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update customization: {str(e)}")


@router.get("/{tenant_id}/analytics")
async def get_embed_analytics(
    tenant_id: str,
    request: Request
):
    """Get analytics for embedded widget usage"""

    try:
        # Validate tenant
        tenant_info = await tenant_manager.get_tenant_by_id(tenant_id)
        if not tenant_info:
            raise HTTPException(status_code=404, detail="Chat instance not found")

        # TODO: Implement real analytics from database
        # For now, return mock data
        analytics = {
            "activeEmbeds": 3,
            "monthlyConversations": 1247,
            "domains": ["example.com", "demo.site", "client.app"],
            "lastUpdated": datetime.now().isoformat(),
            "usage": {
                "today": 45,
                "thisWeek": 312,
                "thisMonth": 1247
            },
            "topDomains": [
                {"domain": "example.com", "conversations": 567},
                {"domain": "demo.site", "conversations": 423},
                {"domain": "client.app", "conversations": 257}
            ]
        }

        return analytics

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


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
        timestamp = usage_data.get("timestamp", datetime.now().isoformat())

        # TODO: Store usage analytics in database
        # For now, just log the usage
        print(f"Widget usage - Tenant: {tenant_id}, Event: {event_type}, Domain: {domain}, Time: {timestamp}")

        return {"success": True, "message": "Usage tracked"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")
