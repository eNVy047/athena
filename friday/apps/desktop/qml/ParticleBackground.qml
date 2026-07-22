import QtQuick

Rectangle {
    id: bg
    color: themeManager.backgroundColor
    
    // Simple animated grid/particles
    Canvas {
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.fillStyle = themeManager.backgroundColor
            ctx.fillRect(0, 0, width, height)
            
            ctx.strokeStyle = Qt.rgba(255, 255, 255, 0.02)
            ctx.lineWidth = 1
            
            for(var i = 0; i < width; i+= 40) {
                ctx.beginPath()
                ctx.moveTo(i, 0)
                ctx.lineTo(i, height)
                ctx.stroke()
            }
            for(var j = 0; j < height; j+= 40) {
                ctx.beginPath()
                ctx.moveTo(0, j)
                ctx.lineTo(width, j)
                ctx.stroke()
            }
        }
    }
}
