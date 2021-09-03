(function(undefined) {
    'use strict';

    if (typeof sigma === 'undefined')
        throw 'sigma is not declared';

    sigma.utils.pkg('sigma.canvas.edgehovers');
    sigma.canvas.edgehovers.vert = function(edge, source, target, context, settings) {
        var color = edge.color,
            prefix = settings('prefix') || '',
            size = settings('edgeHoverSizeRatio') * (edge[prefix + 'size'] || 1),
            edgeColor = settings('edgeColor'),
            defaultNodeColor = settings('defaultNodeColor'),
            defaultEdgeColor = settings('defaultEdgeColor'),
            sX = source[prefix + 'x'],
            sY = source[prefix + 'y'],
            tX = target[prefix + 'x'],
            tY = target[prefix + 'y'];

        if (!color)
            switch (edgeColor) {
                case 'source':
                    color = source.color || defaultNodeColor;
                    break;
                case 'target':
                    color = target.color || defaultNodeColor;
                    break;
                default:
                    color = defaultEdgeColor;
                    break;
            }

        if (settings('edgeHoverColor') === 'edge') {
            color = edge.hover_color || color;
        } else {
            color = edge.hover_color || settings('defaultEdgeHoverColor') || color;
        }

        context.strokeStyle = color;
        context.lineWidth = size;
        context.beginPath();
        context.moveTo(sX, sY);
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
        context.lineTo(tX, tY);
        context.stroke();
    };
}).call(this);