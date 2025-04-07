import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KiaConceptFlux",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only target our specific node
        if (nodeData.name === "KiaConceptClipTextEncodeFlux") {
            // Override the onExecuted method to update the UI
            nodeType.prototype.onExecuted = function(message) {
                console.log("Node executed with message:", message);
                
                if (message && (message.clip_prompt || message.t5xxl_prompt)) {
                    console.log("Updating prompts in UI");
                    
                    // Find the clip_l widget (index 3)
                    if (message.clip_prompt && this.widgets[3]) {
                        console.log("Setting clip_l to:", message.clip_prompt);
                        this.widgets[3].value = message.clip_prompt;
                    }
                    
                    // Find the t5xxl widget (index 4)
                    if (message.t5xxl_prompt && this.widgets[4]) {
                        console.log("Setting t5xxl to:", message.t5xxl_prompt);
                        this.widgets[4].value = message.t5xxl_prompt;
                    }
                    
                    // Force a redraw of the widget
                    app.canvas.setDirty(true, true);
                    
                    // Important: Explicitly notify the node that widgets have changed
                    if (this.onWidgetChanged) {
                        this.onWidgetChanged();
                    }
                }
            };
            
            // Add change listeners to theme and strength
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                const self = this;
                
                // Add event listeners for theme and strength widgets
                if (this.widgets.length >= 2) {
                    // Theme widget (index 0)
                    const origThemeCallback = this.widgets[0].callback;
                    this.widgets[0].callback = function(v) {
                        console.log("Theme changed to:", v);
                        const result = origThemeCallback ? origThemeCallback.call(this, v) : undefined;
                        
                        // Execute the node to update prompts
                        self.graph.runStep(1);
                        
                        return result;
                    };
                    
                    // Strength widget (index 1)
                    const origStrengthCallback = this.widgets[1].callback;
                    this.widgets[1].callback = function(v) {
                        console.log("Strength changed to:", v);
                        const result = origStrengthCallback ? origStrengthCallback.call(this, v) : undefined;
                        
                        // Execute the node to update prompts
                        self.graph.runStep(1);
                        
                        return result;
                    };
                }
                
                // Also add a context menu option
                this.getExtraMenuOptions = function(_, options) {
                    options.push({
                        content: "Refresh Prompts",
                        callback: () => {
                            console.log("Refreshing prompts via context menu");
                            // Force the widgets to be empty to trigger an update
                            if (this.widgets[3]) this.widgets[3].value = "";
                            if (this.widgets[4]) this.widgets[4].value = "";
                            // Execute the node to update prompts
                            this.graph.runStep(1);
                        }
                    });
                };
                
                return result;
            };
        }
    }
});