import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KiaConceptFlux",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "KiaConceptClipTextEncodeFlux") {
            console.log("KiaConceptClipTextEncodeFlux node registered");
            
            // Store original configure method to extend it
            const origConfigure = nodeType.prototype.configure;
            nodeType.prototype.configure = function(info) {
                console.log("Node configured with info:", info);
                if (origConfigure) {
                    origConfigure.call(this, info);
                }
                
                // Make sure we process any UI update that might be in the properties
                if (info.properties && info.properties.ui) {
                    console.log("Processing UI update from properties:", info.properties.ui);
                    this.updatePromptFields(info.properties.ui);
                }
            };
            
            // Add a method to directly update the text fields
            nodeType.prototype.updatePromptFields = function(ui) {
                console.log("updatePromptFields called with:", ui);
                
                if (!ui) {
                    console.log("No UI data provided, skipping update");
                    return;
                }
                
                // Find the clip_l widget (index 3)
                const clipWidget = this.widgets.find(w => w.name === "clip_l") || this.widgets[3];
                if (clipWidget && ui.clip_prompt) {
                    console.log("Setting clip_l widget value to:", ui.clip_prompt.substring(0, 50) + "...");
                    clipWidget.value = ui.clip_prompt;
                }
                
                // Find the t5xxl widget (index 4)
                const t5xxlWidget = this.widgets.find(w => w.name === "t5xxl") || this.widgets[4];
                if (t5xxlWidget && ui.t5xxl_prompt) {
                    console.log("Setting t5xxl widget value to:", ui.t5xxl_prompt.substring(0, 50) + "...");
                    t5xxlWidget.value = ui.t5xxl_prompt;
                }
                
                // Force a widget update
                this.setDirtyCanvas(true, true);
            };
            
            // Override onNodeCreated to set up listeners
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                console.log("Node created");
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                // Store reference to this for callbacks
                const self = this;
                
                // Process the node's current output message (if any)
                if (this.outputs && this.outputs.length > 0 && this.outputs[0].links) {
                    this.outputs[0].links.forEach(linkId => {
                        const link = app.graph.links[linkId];
                        if (link && link.data && link.data.ui) {
                            console.log("Processing initial output data:", link.data.ui);
                            this.updatePromptFields(link.data.ui);
                        }
                    });
                }
                
                // Add direct widget callbacks to theme and strength
                this.widgets.forEach((widget, index) => {
                    console.log(`Widget ${index}: ${widget.name} of type ${widget.type}`);
                    
                    if (widget.name === "theme" || widget.name === "strength") {
                        const origCallback = widget.callback;
                        widget.callback = function(value) {
                            console.log(`Widget ${widget.name} changed to:`, value);
                            const result = origCallback ? origCallback.call(this, value) : undefined;
                            
                            // Queue a node execution
                            setTimeout(() => {
                                console.log(`Triggering execution after ${widget.name} change`);
                                self.triggerSlot(0, null, { force_exec: true });
                            }, 50);
                            
                            return result;
                        };
                    }
                });
                
                return result;
            };
            
            // Override onExecuted to update the UI
            nodeType.prototype.onExecuted = function(message) {
                console.log("Node executed with message:", message);
                
                if (message && message.ui) {
                    console.log("Processing UI update from execution:", message.ui);
                    this.updatePromptFields(message.ui);
                }
            };
            
            // Add a context menu option to refresh
            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                options.push({
                    content: "Refresh Prompts",
                    callback: () => {
                        console.log("Refreshing prompts via context menu");
                        
                        // Reset the text widgets to force an update
                        const clipWidget = this.widgets.find(w => w.name === "clip_l") || this.widgets[3];
                        const t5xxlWidget = this.widgets.find(w => w.name === "t5xxl") || this.widgets[4];
                        
                        if (clipWidget) clipWidget.value = "";
                        if (t5xxlWidget) t5xxlWidget.value = "";
                        
                        // Trigger node execution
                        this.triggerSlot(0, null, { force_exec: true });
                    }
                });
            };
        }
    }
});