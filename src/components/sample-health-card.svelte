<script>
    // This component shows a sample health card with the new format for testing and demonstration
    export let showSample = true;

    const sampleAdvice = `
TOP TIP: Stay hydrated and take frequent breaks in higher temperatures.

WEATHER BRIEF: Mendez is slightly cooler and more humid than Dasmariñas. Be prepared for a potential temperature drop.

HEALTH REMINDERS:
1. Drink plenty of water throughout your journey.
2. Wear light-colored, loose-fitting clothing to stay cool.
3. Apply sunscreen with a high SPF, especially if you'll be outdoors.
4. Bring insect repellent, especially if you plan on hiking.

WATCH FOR:
• Signs of heat exhaustion (dizziness, headache, nausea).
• Any unusual insect bites or stings.

QUICK TIPS:
• Pack a reusable water bottle.
• Use a hat and sunglasses for sun protection.

_Remember to consult a healthcare professional for personalized medical advice._
`;

    function formatAdviceText(text) {
        if (!text) return '';
        
        // Initial cleaning - normalize line endings and ensure proper breaks
        text = text
            // Replace multiple consecutive newlines with two newlines
            .replace(/\n{3,}/g, '\n\n')
            // Ensure line breaks before section headings
            .replace(/([^\n])(TOP TIP|WEATHER BRIEF|HEALTH REMINDERS|WATCH FOR|QUICK TIPS)/g, '$1\n\n$2')
            // Fix numbered list items that appear on the same line
            .replace(/(\d+\.?\)?\s+[^.\n]+\.)(\s*)(\d+\.?\)?\s+)/g, '$1\n$3')
            // Fix bullet points that appear on the same line
            .replace(/([.!?])(\s*)(•|\*|\-)\s+/g, '$1\n$3 ')
            // Add newline before bullet points if they don't have one
            .replace(/([^\n])(•|\*|\-)\s+/g, '$1\n$2 ');
        
        // Split the text into sections
        const sections = {
            topTip: '',
            weatherBrief: '',
            healthReminders: [],
            watchFor: [],
            quickTips: [],
            disclaimer: ''
        };
        
        // Extract the top tip (case insensitive)
        const topTipMatch = text.match(/TOP TIP:?\s*(.*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?$)/is);
        if (topTipMatch && topTipMatch[1]) sections.topTip = topTipMatch[1].trim();
        
        // Extract the weather brief section (case insensitive)
        const weatherBriefMatch = text.match(/WEATHER BRIEF:?\s*([\s\S]*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?HEALTH REMINDERS)/is);
        if (weatherBriefMatch && weatherBriefMatch[1]) {
            // Process multi-line weather briefs and preserve paragraphs
            sections.weatherBrief = weatherBriefMatch[1]
                .trim()
                .split(/\n\n+/)
                .map(para => para.trim().replace(/\n/g, ' '))
                .join('</p><p>');
        }
        
        // Extract health reminders with improved regex (case insensitive)
        const healthRemindersSection = text.match(/HEALTH REMINDERS:?\s*([\s\S]*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?WATCH FOR|$)/is);
        if (healthRemindersSection && healthRemindersSection[1]) {
            // Try to find numbered items first
            const numberedItems = Array.from(
                healthRemindersSection[1].matchAll(/\n?\s*(\d+)\.?\)?\s+(.*?)(?=\n\s*\d+\.?\)?\s+|\n\n|\n?WATCH FOR|$)/gis)
            );
            
            if (numberedItems && numberedItems.length > 0) {
                // Process each numbered match
                sections.healthReminders = numberedItems.map(match => {
                    return match[2].trim().replace(/\n/g, ' ');
                }).filter(item => item.length > 0);
            } else {
                // Fallback to bullet points if no numbers found
                const bulletItems = healthRemindersSection[1]
                    .split(/\n\s*[•\*\-]\s+/)
                    .map(item => item.trim())
                    .filter(item => item.length > 0);
                    
                if (bulletItems.length > 0) {
                    sections.healthReminders = bulletItems;
                } else {
                    // Last resort: just use the whole text as a single item
                    const content = healthRemindersSection[1].trim();
                    if (content) sections.healthReminders = [content];
                }
            }
        }
        
        // Extract Watch For items (case insensitive)
        const watchForSection = text.match(/WATCH FOR:?\s*([\s\S]*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?QUICK TIPS|$)/is);
        if (watchForSection && watchForSection[1]) {
            // Try to find bullet points
            const bulletItems = watchForSection[1]
                .split(/\n\s*[•\*\-]\s+/)
                .slice(1) // Skip the first empty item
                .map(item => item.trim().replace(/\n([^•\*\-])/g, ' $1')) // Join multi-line items
                .filter(item => item.length > 0);
                
            if (bulletItems.length > 0) {
                sections.watchFor = bulletItems;
            } else {
                // If no bullet points, split by line breaks
                const lines = watchForSection[1]
                    .split(/\n+/)
                    .map(line => line.trim())
                    .filter(line => line.length > 0);
                    
                if (lines.length > 0) {
                    sections.watchFor = lines;
                } else {
                    // Last resort
                    const content = watchForSection[1].trim();
                    if (content) sections.watchFor = [content];
                }
            }
        }
        
        // Extract Quick Tips items (case insensitive)
        const quickTipsSection = text.match(/QUICK TIPS:?\s*([\s\S]*?)(?:\n\n|\n(?=[A-Z][A-Z])|\n?_|$)/is);
        if (quickTipsSection && quickTipsSection[1]) {
            // Try to find bullet points
            const bulletItems = quickTipsSection[1]
                .split(/\n\s*[•\*\-]\s+/)
                .slice(1) // Skip the first empty item
                .map(item => item.trim().replace(/\n([^•\*\-])/g, ' $1')) // Join multi-line items
                .filter(item => item.length > 0);
                
            if (bulletItems.length > 0) {
                sections.quickTips = bulletItems;
            } else {
                // If no bullet points, split by line breaks
                const lines = quickTipsSection[1]
                    .split(/\n+/)
                    .map(line => line.trim())
                    .filter(line => line.length > 0);
                    
                if (lines.length > 0) {
                    sections.quickTips = lines;
                } else {
                    // Last resort
                    const content = quickTipsSection[1].trim();
                    if (content) sections.quickTips = [content];
                }
            }
        }
        
        // Extract disclaimer - usually the last paragraph or anything with "remember" or starting with _
        const disclaimerMatch = text.match(/(?:_|remember|note:|disclaimer:)(.*?)(?:$|\.?$)/is);
        if (disclaimerMatch && disclaimerMatch[1]) {
            sections.disclaimer = disclaimerMatch[1].trim();
        }

        // Now build the HTML with the structured sections
        let formattedHtml = '';
        
        // Top Tip 
        if (sections.topTip) {
            formattedHtml += `<div class="top-tip"><span class="tip-label">TOP TIP</span> ${sections.topTip}</div>`;
        }
        
        // Weather Brief
        if (sections.weatherBrief) {
            formattedHtml += `<div class="tile weather-brief">
                <div class="tile-header">WEATHER BRIEF</div>
                <div class="tile-content"><p>${sections.weatherBrief}</p></div>
            </div>`;
        }
        
        // Health Reminders
        if (sections.healthReminders.length > 0) {
            formattedHtml += `<div class="tile health-reminders">
                <div class="tile-header">HEALTH REMINDERS</div>
                <div class="tile-content">
                    <ol>`;
            sections.healthReminders.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ol>
                </div>
            </div>`;
        }
        
        // Watch For
        if (sections.watchFor.length > 0) {
            formattedHtml += `<div class="tile watch-for">
                <div class="tile-header">WATCH FOR</div>
                <div class="tile-content">
                    <ul class="warning-list">`;
            sections.watchFor.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ul>
                </div>
            </div>`;
        }
        
        // Quick Tips
        if (sections.quickTips.length > 0) {
            formattedHtml += `<div class="tile quick-tips">
                <div class="tile-header">QUICK TIPS</div>
                <div class="tile-content">
                    <ul class="tips-list">`;
            sections.quickTips.forEach(point => {
                if (point) formattedHtml += `<li>${point}</li>`;
            });
            formattedHtml += `</ul>
                </div>
            </div>`;
        }
        
        return formattedHtml;
    }
</script>

{#if showSample}
<div class="sample-card-container">
    <div class="health-advice-card">
        <div class="card-header">
            <h3>Travel Health Tips</h3>
            <div class="route">
                <span class="city origin">Manila</span>
                <span class="arrow">→</span>
                <span class="city destination">Tagaytay</span>
            </div>
        </div>
        
        <div class="card-body">
            <div class="advice-content">
                {@html formatAdviceText(sampleAdvice)}
            </div>
        </div>
        
        <div class="card-footer">
            <div class="disclaimer">
                Always consult a healthcare professional for personalized medical advice.
            </div>
            <div class="update-time">
                Updated: {new Date().toLocaleString()}
            </div>
        </div>
    </div>
    
    <div class="sample-notice">
        <p>This is a sample card showing the new health advice format.</p>
        <button on:click={() => showSample = false}>Hide Sample</button>
    </div>
</div>
{/if}

<style>
    .sample-card-container {
        margin: 1.5rem 0;
        position: relative;
    }
    
    .health-advice-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        overflow: hidden;
        margin: 0 auto;
        width: 100%;
    }
    
    .card-header {
        background: #dd815e; /* Updated to orange theme */
        color: white;
        padding: 1rem;
        border-radius: 8px 8px 0 0;
    }
    
    .card-header h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.4rem;
    }
    
    .route {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .city {
        font-weight: 600;
    }
    
    .origin {
        color: #fff; /* Full white for better readability */
    }
    
    .destination {
        color: #fff; /* Full white for better readability */
    }
    
    .arrow {
        margin: 0 0.5rem;
        font-size: 1.2rem;
    }
    
    .card-body {
        padding: 1rem;
    }
    
    .advice-content {
        color: #333;
        line-height: 1.5;
    }
    
    .top-tip {
        background-color: #f8f0ec; /* Light orange background */
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        font-weight: 500;
        color: #b35d3a; /* Darker orange for text */
        border-left: 4px solid #dd815e;
    }
    
    .tip-label {
        background: #dd815e; /* Orange theme */
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.5rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .advice-content h3 {
        color: #b35d3a; /* Darker orange for headers */
        font-size: 1rem;
        margin: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #f8f0ec; /* Light orange border */
        padding-bottom: 0.3rem;
    }
    
    .weather-brief {
        margin-bottom: 1rem;
    }
    
    .weather-brief p {
        margin: 0.5rem 0;
    }
    
    .health-reminders ol {
        padding-left: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .health-reminders li {
        margin-bottom: 0.5rem;
    }
    
    .warning-list, .tips-list {
        list-style-type: none;
        padding-left: 0;
        margin: 0.5rem 0;
    }
    
    .warning-list li {
        position: relative;
        padding-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .warning-list li:before {
        content: "⚠️";
        position: absolute;
        left: 0;
        top: 0;
        font-size: 0.9rem;
    }
    
    .tips-list li {
        position: relative;
        padding-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .tips-list li:before {
        content: "✓";
        position: absolute;
        left: 0.2rem;
        top: -1px;
        font-weight: bold;
        color: #dd815e; /* Updated to orange theme */
    }
    
    .card-footer {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-top: 1px solid #f8f0ec; /* Light orange border */
        font-size: 0.8rem;
        color: #666;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .disclaimer {
        font-style: italic;
        flex: 1;
    }
    
    .update-time {
        color: #888;
        font-size: 0.75rem;
    }
    
    .sample-notice {
        margin-top: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background-color: #f8f0ec; /* Light orange background */
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    .sample-notice button {
        background: #dd815e; /* Orange theme */
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
    }
    
    .sample-notice button:hover {
        background-color: #c26744; /* Darker orange on hover */
    }

    .tile {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
        overflow: hidden;
    }

    .tile-header {
        background-color: #3273dc;
        color: white;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 14px;
        letter-spacing: 0.5px;
    }

    .tile-content {
        padding: 15px;
    }

    .weather-brief .tile-header {
        background-color: #3273dc; /* Blue for weather */
    }

    .health-reminders .tile-header {
        background-color: #48c774; /* Green for health */
    }

    .watch-for .tile-header {
        background-color: #ff3860; /* Red for warnings */
    }

    .quick-tips .tile-header {
        background-color: #ffdd57; /* Yellow for tips */
        color: #363636;
    }

    .health-reminders ol,
    .watch-for ul,
    .quick-tips ul {
        margin: 0;
        padding-left: 20px;
    }

    .health-reminders li,
    .watch-for li,
    .quick-tips li {
        margin-bottom: 8px;
    }

    .health-reminders li:last-child,
    .watch-for li:last-child,
    .quick-tips li:last-child {
        margin-bottom: 0;
    }
</style>
