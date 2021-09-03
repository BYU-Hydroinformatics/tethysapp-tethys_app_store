(function(undefined) {
    'use strict';

    if (typeof sigma === 'undefined')
        throw 'sigma is not declared';

    sigma.utils.pkg('sigma.canvas.edges');
    sigma.canvas.edges.vert = function(edge, source, target, context, settings) {
        let color = edge.color,
            prefix = settings('prefix') || '';

        context.strokeStyle = color;
        context.lineWidth = edge[prefix + 'size'];

        context.beginPath();
        context.moveTo(
            source[prefix + 'x'],
            source[prefix + 'y']
        );

        let verticies = edge.vert;

        for (let i = 0; i < verticies.length; ++i) {
            try {
                let nodesOnScreen = s.renderers["0"].nodesOnScreen;
                let nextVert = nodesOnScreen.find(node => node.epaId === verticies[i]);

                context.lineTo(
                    nextVert[prefix + 'x'],
                    nextVert[prefix + 'y']
                );
            }
            catch (e) {
                // nothing
            }
        }

        context.lineTo(
            target[prefix + 'x'],
            target[prefix + 'y']
        );

        context.stroke();
    };
}).call(this);