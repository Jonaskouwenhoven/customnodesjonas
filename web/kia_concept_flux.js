import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KiaConceptFlux",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "KiaConceptClipTextEncodeFlux") {
            // Add a widget dynamically for clip_l and t5xxl
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                const self = this;
                
                // Add clip_l widget
                this.addWidget("text", "clip_l", "", function(v) {
                    // Handle value changes
                }, { multiline: true });
                
                // Add t5xxl widget
                this.addWidget("text", "t5xxl", "", function(v) {
                    // Handle value changes
                }, { multiline: true });
                
                // We need to update the UI when inputs are changed
                this.onExecuted = function(message) {
                    if (message && message.clip_prompt) {
                        self.widgets[3].value = message.clip_prompt;
                    }
                    if (message && message.t5xxl_prompt) {
                        self.widgets[4].value = message.t5xxl_prompt;
                    }
                };
                
                return result;
            };
            
            // Override the original getExtraMenuOptions
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                if (getExtraMenuOptions) {
                    getExtraMenuOptions.apply(this, arguments);
                }
                
                // Add a refresh option in the context menu
                options.push({
                    content: "Refresh Prompts",
                    callback: () => {
                        // Trigger a re-execution of the node
                        this.setDirtyCanvas(true, true);
                        this.onExecuted();
                    }
                });
            };
        }
    }
});