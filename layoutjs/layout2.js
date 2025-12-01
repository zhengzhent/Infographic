// layout.js
;(function () {
  // ==== 配置图片路径 ====
  const TEXT_IMAGE_URL = '../transparent_image/text_GPTimage_trimed_trans.png' // 文本图片
  const ILLUSTRATION_URL =
    '../transparent_image/illus_GPTimage_trimed_trans.png' // illustration image

  // 等页面和原始 chart JS 都执行完
  window.addEventListener('load', () => {
    const svgSel = d3.select('#chart-container svg')
    if (svgSel.empty()) {
      console.warn('[layout] 未找到 #chart-container 下的 svg')
      return
    }

    const canvasWidth =
      parseFloat(svgSel.attr('width')) || svgSel.node().viewBox.baseVal.width
    const canvasHeight =
      parseFloat(svgSel.attr('height')) || svgSel.node().viewBox.baseVal.height

    // 先加载 text image，拿到长宽比
    const textImg = new Image()
    textImg.onload = () => {
      const textAspect = textImg.width / textImg.height || 4 // 容错
      runLayout(svgSel, canvasWidth, canvasHeight, textAspect, textImg)
    }
    textImg.onerror = () => {
      console.error('[layout] text image 加载失败，使用 4:1 默认比例')
      runLayout(svgSel, canvasWidth, canvasHeight, 4, null)
    }
    textImg.src = TEXT_IMAGE_URL
  })

  async function runLayout(
    svgSel,
    canvasWidth,
    canvasHeight,
    textAspect,
    textImg,
  ) {
    // 1. 从当前 SVG 生成初始 mask（只算图表，不含后面插入的图片）
    const rawMask = await generateMaskFromSvg(svgSel, canvasWidth, canvasHeight)
    let maskObj = makeMaskObj(rawMask.mask, rawMask.width, rawMask.height)

    // 2. 在 mask=0 中查找固定比例的最大矩形：text image
    const textRect = findLargestRectWithRatio(maskObj, textAspect, {
      minSize: 80, // 最小高度/宽度
      step: 4, // 网格步长，值越小越精细但越慢
    })

    if (textRect) {
      console.log('[layout] text image rect:', textRect)
      // 把 text image 塞进去（保持比例，已由搜索保证）
      if (textImg) {
        svgSel
          .append('image')
          .attr('href', TEXT_IMAGE_URL)
          .attr('x', textRect.x)
          .attr('y', textRect.y)
          .attr('width', textRect.w)
          .attr('height', textRect.h)

        // 根据 textImg 的 alpha 通道更新 mask：
        // 只有非透明像素才标记为 1，透明区域仍可用于 illustration
        fillMaskWithImageAlpha(maskObj, textRect, textImg)
      } else {
        // 如果没有图片就画个占位矩形，并整块占用
        drawDebugRect(svgSel, textRect, 'rgba(160, 160, 255, 0.6)', 'TEXT')
        fillMaskRect(maskObj, textRect)
      }
    } else {
      console.warn('[layout] 没有找到放 text image 的区域')
    }

    // 3. 在更新后的 mask 上，用 1:1 比例寻找最大正方形：illustration
    const squareRect = findLargestRectWithRatio(maskObj, 1.0, {
      minSize: 80,
      step: 4,
    })

    if (squareRect) {
      console.log('[layout] illustration rect:', squareRect)

      // 插画图片（等比缩放到这个正方形）
      if (ILLUSTRATION_URL) {
        svgSel
          .append('image')
          .attr('href', ILLUSTRATION_URL)
          .attr('x', squareRect.x)
          .attr('y', squareRect.y)
          .attr('width', squareRect.w)
          .attr('height', squareRect.h)
      } else {
        drawDebugRect(svgSel, squareRect, 'rgba(255, 200, 120, 0.6)', 'ILLO')
      }

      // illustration 这里直接用整块矩形占用即可
      fillMaskRect(maskObj, squareRect)
    } else {
      console.warn('[layout] 没有找到放 illustration 的正方形区域')
    }
  }

  // ============== mask & 搜索相关函数 ==============

  // 从 SVG 生成 mask: 1=有图表像素，0=空
  function generateMaskFromSvg(svgSelection, width, height) {
    return new Promise((resolve, reject) => {
      try {
        const svgNode = svgSelection.node()
        const cloned = svgNode.cloneNode(true)

        // 去掉根 svg 的 style，避免背景色影响
        cloned.removeAttribute('style')

        const serializer = new XMLSerializer()
        let svgStr = serializer.serializeToString(cloned)
        if (!svgStr.includes('xmlns="http://www.w3.org/2000/svg"')) {
          svgStr = svgStr.replace(
            '<svg',
            '<svg xmlns="http://www.w3.org/2000/svg"',
          )
        }

        const imgSrc =
          'data:image/svg+xml;base64,' +
          btoa(unescape(encodeURIComponent(svgStr)))

        const img = new Image()
        img.onload = () => {
          const canvas = document.createElement('canvas')
          canvas.width = width
          canvas.height = height
          const ctx = canvas.getContext('2d')
          ctx.clearRect(0, 0, width, height)
          ctx.drawImage(img, 0, 0)

          const imageData = ctx.getImageData(0, 0, width, height)
          const data = imageData.data

          const mask = new Uint8Array(width * height)
          let ones = 0
          for (let i = 0; i < mask.length; i++) {
            const alpha = data[i * 4 + 3]
            if (alpha > 0) {
              mask[i] = 1
              ones++
            }
          }

          console.log(
            '[layout] mask generated: ones =',
            ones,
            'ratio =',
            ones / mask.length,
          )
          resolve({ mask, width, height })
        }
        img.onerror = reject
        img.src = imgSrc
      } catch (e) {
        reject(e)
      }
    })
  }

  // 把 mask + 前缀和封装到对象里
  function makeMaskObj(mask, width, height) {
    return {
      mask,
      width,
      height,
      prefix: buildPrefix(mask, width, height),
    }
  }

  // 前缀和（积分图），支持 O(1) 求任意矩形和
  function buildPrefix(mask, width, height) {
    const stride = width + 1
    const prefix = new Uint32Array((height + 1) * stride)

    for (let y = 0; y < height; y++) {
      let rowSum = 0
      const rowOffsetMask = y * width
      const rowOffsetPrefix = (y + 1) * stride
      const prevRowOffsetPrefix = y * stride

      for (let x = 0; x < width; x++) {
        rowSum += mask[rowOffsetMask + x]
        prefix[rowOffsetPrefix + x + 1] =
          prefix[prevRowOffsetPrefix + x + 1] + rowSum
      }
    }
    return prefix
  }

  // 矩形内 mask 的和（>0 说明有占用）
  function rectSum(maskObj, x, y, w, h) {
    const { prefix, width } = maskObj
    const stride = width + 1
    const x1 = Math.floor(x)
    const y1 = Math.floor(y)
    const x2 = Math.floor(x + w)
    const y2 = Math.floor(y + h)

    const A = prefix[y1 * stride + x1]
    const B = prefix[y1 * stride + x2]
    const C = prefix[y2 * stride + x1]
    const D = prefix[y2 * stride + x2]
    return D - B - C + A
  }

  // 根据一张 image（带透明通道）更新 mask：
  // 只把 alpha > 0 的像素对应的位置置为 1
  function fillMaskWithImageAlpha(maskObj, rect, img) {
    const { mask, width, height } = maskObj

    const rectW = Math.max(0, Math.floor(rect.w))
    const rectH = Math.max(0, Math.floor(rect.h))
    if (rectW === 0 || rectH === 0) return

    const canvas = document.createElement('canvas')
    canvas.width = rectW
    canvas.height = rectH
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, rectW, rectH)
    // 将 img 缩放到 rect 尺寸
    ctx.drawImage(img, 0, 0, rectW, rectH)

    const imageData = ctx.getImageData(0, 0, rectW, rectH)
    const data = imageData.data

    const startX = Math.max(0, Math.floor(rect.x))
    const startY = Math.max(0, Math.floor(rect.y))

    for (let y = 0; y < rectH && startY + y < height; y++) {
      const rowOffsetMask = (startY + y) * width
      const rowOffsetImg = y * rectW
      for (let x = 0; x < rectW && startX + x < width; x++) {
        const alpha = data[(rowOffsetImg + x) * 4 + 3]
        if (alpha > 0) {
          mask[rowOffsetMask + startX + x] = 1
        }
      }
    }

    // 重建前缀和
    maskObj.prefix = buildPrefix(maskObj.mask, width, height)
  }

  // 更新 mask（把 rect 区域整块置为 1），并重建前缀和
  function fillMaskRect(maskObj, rect) {
    const { mask, width, height } = maskObj
    const xi = Math.max(0, Math.floor(rect.x))
    const yi = Math.max(0, Math.floor(rect.y))
    const wi = Math.max(0, Math.floor(rect.w))
    const hi = Math.max(0, Math.floor(rect.h))

    for (let y = xi; y < yi + hi && y < height; y++) {
      const rowOffset = y * width
      for (let x = xi; x < xi + wi && x < width; x++) {
        mask[rowOffset + x] = 1
      }
    }
    // 重建前缀和
    maskObj.prefix = buildPrefix(maskObj.mask, width, height)
  }

  // 在 mask=0 中，用固定长宽比 aspectRatio 找“最大矩形”
  function findLargestRectWithRatio(maskObj, aspectRatio, options = {}) {
    const { width, height } = maskObj
    const minSize = options.minSize || 40
    const step = options.step || 4

    // 最大可能高度 = 受画布尺寸 & 比例限制
    const maxH = Math.floor(Math.min(height, width / aspectRatio))

    for (let h = maxH; h >= minSize; h -= step) {
      const w = Math.floor(h * aspectRatio)
      if (w < minSize || w > width) continue

      for (let y = 0; y <= height - h; y += step) {
        for (let x = 0; x <= width - w; x += step) {
          if (rectSum(maskObj, x, y, w, h) === 0) {
            // 第一次找到的就是当前高度下的最大面积；
            // 因为我们从大到小遍历高度，这是近似的“最大矩形”
            return { x, y, w, h }
          }
        }
      }
    }
    return null
  }

  // 调试可视化用，不需要可删
  function drawDebugRect(svgSel, rect, color, label) {
    svgSel
      .append('rect')
      .attr('x', rect.x)
      .attr('y', rect.y)
      .attr('width', rect.w)
      .attr('height', rect.h)
      .attr('fill', color)
      .attr('stroke', 'black')
      .attr('stroke-width', 1)
      .attr('opacity', 0.7)

    if (label) {
      svgSel
        .append('text')
        .attr('x', rect.x + 8)
        .attr('y', rect.y + 20)
        .text(label)
        .attr('fill', '#333')
        .attr('font-size', 14)
        .attr('font-family', 'sans-serif')
    }
  }
})()
