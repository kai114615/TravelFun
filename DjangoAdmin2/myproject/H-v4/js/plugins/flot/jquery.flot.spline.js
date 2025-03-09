/**
 * Flot plugin that provides spline interpolation for line graphs
 * author: Alex Bardas < alex.bardas@gmail.com >
 * modified by: Avi Kohn https://github.com/AMKohn
 * based on the spline interpolation described at:
 *		 http://scaledinnovation.com/analytics/splines/aboutSplines.html
 *
 * Example usage: (add in plot options series object)
 *		for linespline:
 *			series: {
 *				...
 *				lines: {
 *					show: false
 *				},
 *				splines: {
 *					show: true,
 *					tension: x, (float between 0 and 1, defaults to 0.5),
 *					lineWidth: y (number, defaults to 2),
 *					fill: z (float between 0 .. 1 or false, as in flot documentation)
 *				},
 *				...
 *			}
 *		areaspline:
 *			series: {
 *				...
 *				lines: {
 *					show: true,
 *					lineWidth: 0, (line drawing will not execute)
 *					fill: x, (float between 0 .. 1, as in flot documentation)
 *					...
 *				},
 *				splines: {
 *					show: true,
 *					tension: 0.5 (float between 0 and 1)
 *				},
 *				...
 *			}
 *
 */

(function ($) {
  'use strict'

  /**
   * @param {number} x0, y0, x1, y1: coordinates of the end (knot) points of the segment
   * @param {number} x2, y2: the next knot (not connected, but needed to calculate p2)
   * @param {number} tension: control how far the control points spread
   * @return {Array}: p1 -> control point, from x1 back toward x0
   * 					p2 -> the next control point, returned to become the next segment's p1
   *
   * @api private
   */
  function getControlPoints(x0, y0, x1, y1, x2, y2, tension) {
    const pow = Math.pow;
    const sqrt = Math.sqrt;
    let d01; let d12; let fa; let fb; let p1x; let p1y; let p2x; let p2y;

    //  Scaling factors: distances from this knot to the previous and following knots.
    d01 = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    d12 = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    fa = tension * d01 / (d01 + d12);
    fb = tension - fa;

    p1x = x1 + fa * (x0 - x2);
    p1y = y1 + fa * (y0 - y2);

    p2x = x1 - fb * (x0 - x2);
    p2y = y1 - fb * (y0 - y2);

    return [p1x, p1y, p2x, p2y];
  }

  let line = [];

  function drawLine(points, ctx, height, fill, seriesColor) {
    let c = $.color.parse(seriesColor);

    c.a = typeof fill == 'number' ? fill : 0.3
    c.normalize();
    c = c.toString();

    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);

    const plength = points.length

    for (let i = 0; i < plength; i++) {
      ctx[points[i][3]].apply(ctx, points[i][2]);
    }

    ctx.stroke();

    ctx.lineWidth = 0;
    ctx.lineTo(points[plength - 1][0], height);
    ctx.lineTo(points[0][0], height);

    ctx.closePath();

    if (fill !== false) {
      ctx.fillStyle = c;
      ctx.fill();
    }
  }

  /**
   * @param {object} ctx: canvas context
   * @param {string} type: accepted strings: 'bezier' or 'quadratic' (defaults to quadratic)
   * @param {Array} points: 2 points for which to draw the interpolation
   * @param {Array} cpoints: control points for those segment points
   *
   * @api private
   */
  function queue(ctx, type, points, cpoints) {
    if (type === void 0 || (type !== 'bezier' && type !== 'quadratic')) {
      type = 'quadratic';
    }
    type = `${type}CurveTo`

    if (line.length == 0) { line.push([points[0], points[1], cpoints.concat(points.slice(2)), type])
    }
    else if (type == 'quadraticCurveTo' && points.length == 2) {
      cpoints = cpoints.slice(0, 2).concat(points);

      line.push([points[0], points[1], cpoints, type]);
    }
    else { line.push([points[2], points[3], cpoints.concat(points.slice(2)), type])
    }
  }

  /**
   * @param {object} plot
   * @param {object} ctx: canvas context
   * @param {object} series
   *
   * @api private
   */

  function drawSpline(plot, ctx, series) {
    // Not interested if spline is not requested
    if (series.splines.show !== true) {
      return
    }

    let cp = []
    // array of control points
    const tension = series.splines.tension || 0.5;
    let idx; let x; let y; const points = series.datapoints.points;
    const ps = series.datapoints.pointsize;
    const plotOffset = plot.getPlotOffset();
    let len = points.length
    const pts = []

    line = [];

    // Cannot display a linespline/areaspline if there are less than 3 points
    if (len / ps < 4) {
      $.extend(series.lines, series.splines);
      return;
    }

    for (idx = 0; idx < len; idx += ps) {
      x = points[idx];
      y = points[idx + 1];
      if (x == null || x < series.xaxis.min || x > series.xaxis.max || y < series.yaxis.min || y > series.yaxis.max) {
        continue
      }

      pts.push(series.xaxis.p2c(x) + plotOffset.left, series.yaxis.p2c(y) + plotOffset.top);
    }

    len = pts.length;

    // Draw an open curve, not connected at the ends
    for (idx = 0; idx < len - 2; idx += 2) {
      cp = cp.concat(getControlPoints.apply(this, pts.slice(idx, idx + 6).concat([tension])));
    }

    ctx.save();
    ctx.strokeStyle = series.color;
    ctx.lineWidth = series.splines.lineWidth;

    queue(ctx, 'quadratic', pts.slice(0, 4), cp.slice(0, 2));

    for (idx = 2; idx < len - 3; idx += 2) {
      queue(ctx, 'bezier', pts.slice(idx, idx + 4), cp.slice(2 * idx - 2, 2 * idx + 2));
    }

    queue(ctx, 'quadratic', pts.slice(len - 2, len), [cp[2 * len - 10], cp[2 * len - 9], pts[len - 4], pts[len - 3]]);

    drawLine(line, ctx, plot.height() + 10, series.splines.fill, series.color);

    ctx.restore();
  }

  $.plot.plugins.push({
    init (plot) {
      plot.hooks.drawSeries.push(drawSpline)
    },
    options: {
      series: {
        splines: {
          show: false,
          lineWidth: 2,
          tension: 0.5,
          fill: false
        }
      }
    },
    name: 'spline',
    version: '0.8.2'
  });
})(jQuery);
