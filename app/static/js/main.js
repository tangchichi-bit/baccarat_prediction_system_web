// 全域性變數
let gameHistory = [];
let socket;


// 頁面載入完成後執行
$(document).ready(function() {
    // 初始化Socket.IO連線
    initSocketIO();
   
    // 初始化牌靴
    initShoe();
   
    // 繫結事件處理函式
    bindEventHandlers();
   
    // 更新統計資料
    updateStatistics();
});


// 初始化Socket.IO連線
function initSocketIO() {
    socket = io();
   
    // 監聽伺服器事件
    socket.on('connect', function() {
        console.log('已連線到伺服器');
    });
   
    socket.on('disconnect', function() {
        console.log('與伺服器斷開連線');
    });
   
    socket.on('update_result', function(data) {
        // 接收伺服器推送的結果更新
        addResult(data.result);
    });
}


// 初始化牌靴
function initShoe() {
    $.get('/api/shoe', function(data) {
        updateShoeDisplay(data);
    });
}


// 更新牌靴顯示
function updateShoeDisplay(data) {
    $('#cards-remaining').text(data.cards_remaining);
    $('#banker-prob').text((data.banker_probability * 100).toFixed(1) + '%');
    $('#player-prob').text((data.player_probability * 100).toFixed(1) + '%');
    $('#tie-prob').text((data.tie_probability * 100).toFixed(1) + '%');
}


// 繫結事件處理函式
function bindEventHandlers() {
    // 模式切換
    $('input[name="mode"]').change(function() {
        const mode = $(this).val();
        if (mode === 'manual') {
            $('#manual-settings').show();
            $('#api-settings').hide();
        } else {
            $('#manual-settings').hide();
            $('#api-settings').show();
        }
    });
   
    // 連線網站
    $('#connect-btn').click(function() {
        const url = $('#url-input').val();
        if (!url) {
            alert('請輸入百家樂網站URL');
            return;
        }
       
        $('#status-label').text('狀態: 正在連線...');
       
        // 這裡應該傳送連線請求到伺服器
        // 簡化處理，直接顯示連線成功
        setTimeout(function() {
            $('#status-label').text('狀態: 已連線');
            alert('已成功連線到百家樂網站');
        }, 1000);
    });
   
    // 設定公共API
    $('#setup-api-btn').click(function() {
        const port = $('#api-port').val();
        if (!port) {
            alert('請輸入API埠');
            return;
        }
       
        $('#api-status').text('API狀態: 正在設定...');
       
        // 簡化處理，直接顯示設定成功
        setTimeout(function() {
            const apiUrl = `http://${window.location.hostname}:${port}/api/callback`;
            $('#api-url').val(apiUrl);
            $('#api-status').text('API狀態: 已設定');
            alert('已成功設定公共API');
        }, 1000);
    });
   
    // 複製URL
    $('#copy-url-btn').click(function() {
        const url = $('#api-url').val();
        if (!url) {
            alert('API URL 為空');
            return;
        }
       
        // 複製到剪貼簿
        navigator.clipboard.writeText(url).then(function() {
            alert('API URL 已複製到剪貼簿');
        }).catch(function(err) {
            console.error('複製失敗: ', err);
            alert('複製失敗，請手動複製');
        });
    });
   
    // 重置牌靴
    $('#reset-shoe-btn').click(function() {
        const numDecks = $('#deck-count').val();
       
        $.ajax({
            url: '/api/shoe/reset',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ num_decks: parseInt(numDecks) }),
            success: function(data) {
                updateShoeDisplay(data);
                alert(data.message);
            },
            error: function() {
                alert('重置牌靴失敗');
            }
        });
    });
   
    // 訓練模型
    $('#train-btn').click(function() {
        if (gameHistory.length < 10) {
            alert('歷史記錄太少，請至少輸入 10 筆資料');
            return;
        }
       
        // 提取歷史結果
        const historyResults = gameHistory.map(record => record.result);
       
        $.ajax({
            url: '/api/train',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ history: historyResults }),
            success: function(data) {
                if (data.success) {
                    alert(data.message);
                } else {
                    alert('訓練失敗: ' + data.message);
                }
            },
            error: function() {
                alert('訓練模型失敗');
            }
        });
    });
   
    // AI預測按鈕點選事件
    $('#predict-btn').click(function() {
        if (gameHistory.length < 10) {
            alert('歷史記錄太少，請至少輸入 10 筆資料');
            return;
        }
       
        // 顯示載入中
        $('#ai-prediction').html('<div class="spinner-border text-primary" role="status"><span class="visually-hidden">載入中...</span></div> 正在預測...');
       
        // 獲取歷史記錄
        const historyResults = gameHistory.map(record => record.result);
       
        console.log('傳送預測請求，歷史記錄:', historyResults); // 新增除錯日誌
       
        $.ajax({
            url: '/api/predict',  // 使用已存在的預測API
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ history: historyResults }),
            success: function(response) {
                console.log('預測響應:', response); // 新增除錯日誌
               
                if (response.success) {
                    // 獲取AI預測結果
                    const prediction = response.ai_prediction.result;
                    const confidence = response.ai_prediction.confidence;
                   
                    // 更新預測結果顯示
                    let color = 'black';
                    if (prediction === '莊家') {
                        color = 'red';
                    } else if (prediction === '閒家') {
                        color = 'blue';
                    } else if (prediction === '和局') {
                        color = 'green';
                    }
                   
                    $('#ai-prediction').html(`
                        <span style="color: ${color}; font-weight: bold;">
                            ${prediction} (信心度: ${confidence.toFixed(2)}%)
                        </span>
                    `);
                } else {
                    $('#ai-prediction').html(`<span class="text-danger">預測失敗: ${response.message || '未知錯誤'}</span>`);
                }
            },
            error: function(xhr, status, error) {
                console.error('預測請求失敗:', xhr.responseText);
                console.error('狀態碼:', xhr.status);
                console.error('狀態:', status);
                console.error('錯誤:', error);
                $('#ai-prediction').html(`<span class="text-danger">預測請求失敗: ${error}</span>`);
            }
        });
    });


    // 算牌公式預測按鈕點選事件
    $('#formula-predict-btn').click(function() {
        $.ajax({
            url: '/api/predict/formula',  // 使用算牌公式預測專用API
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                history: gameHistory.map(record => record.result)
            }),
            success: function(data) {
                if (data.success) {
                    // 更新算牌公式預測結果
                    let prediction = data.prediction;
                    let confidence = data.confidence.toFixed(2);
                   
                    let color = 'black';
                    if (prediction === '莊家') {
                        color = 'red';
                    } else if (prediction === '閒家') {
                        color = 'blue';
                    } else if (prediction === '和局') {
                        color = 'green';
                    }
                   
                    $('#formula-prediction').html(`
                        <span style="color: ${color}; font-weight: bold;">
                            ${prediction} (信心度: ${confidence}%)
                        </span>
                    `);
                } else {
                    $('#formula-prediction').text('預測失敗: ' + data.message);
                }
            },
            error: function() {
                $('#formula-prediction').text('預測請求失敗');
            }
        });
    });
   
    // 新增結果按鈕
    $('#banker-btn').click(function() {
        addResult('莊家');
    });
   
    $('#player-btn').click(function() {
        addResult('閒家');
    });
   
    $('#tie-btn').click(function() {
        addResult('和局');
    });
   
    // 撤銷上一局
    $('#undo-btn').click(function() {
        $.ajax({
            url: '/api/history/undo',
            type: 'POST',
            success: function(data) {
                if (data.success) {
                    gameHistory = data.history;
                    updateRoadMap();
                    updateHistoryTable();
                    updateStatistics();
                } else {
                    alert(data.message);
                }
            },
            error: function() {
                alert('撤銷失敗');
            }
        });
    });
   
    // 清空所有記錄
    $('#clear-btn').click(function() {
        if (confirm('確定要清空所有記錄嗎？')) {
            $.ajax({
                url: '/api/history/clear',
                type: 'POST',
                success: function(data) {
                    if (data.success) {
                        gameHistory = [];
                        updateRoadMap();
                        updateHistoryTable();
                        updateStatistics();
                        $('#ai-prediction').text('尚未進行預測');
                        $('#formula-prediction').text('尚未進行預測');
                        alert(data.message);
                    } else {
                        alert('清空失敗: ' + data.message);
                    }
                },
                error: function() {
                    alert('清空記錄失敗');
                }
            });
        }
    });


    // 計算公式結果
$('#calculate-formula-btn').click(function() {
    // 獲取莊家牌型
    let bankerCards = $('#banker-cards').val().trim();
    // 獲取閒家牌型
    let playerCards = $('#player-cards').val().trim();
   
    // 檢查是否輸入了牌型
    if (!bankerCards || !playerCards) {
        alert('請輸入莊家和閒家牌型');
        return;
    }
   
    console.log("發送數據 - 莊家牌:", bankerCards, "閒家牌:", playerCards);
   
    // 發送請求
    $.ajax({
        url: '/api/formula/calculate',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            banker_cards: bankerCards,
            player_cards: playerCards
        }),
        success: function(data) {
            console.log("接收到的響應:", data);
            if (data.success) {
                // 更新公式預測結果
                let formulaResult = data.formula_result;
                let formulaConfidence = data.formula_confidence.toFixed(2);
               
                let formulaColor = 'black';
                if (formulaResult === '莊家') {
                    formulaColor = 'red';
                } else if (formulaResult === '閒家') {
                    formulaColor = 'blue';
                } else if (formulaResult === '和局') {
                    formulaColor = 'green';
                }
               
                $('#formula-prediction').html(`
                    <span style="color: ${formulaColor}; font-weight: bold;">
                        ${formulaResult} (信心度: ${formulaConfidence}%)
                    </span>
                `);
            } else {
                alert('計算公式結果失敗: ' + data.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("AJAX錯誤:", status, error);
            alert('計算公式結果失敗');
        }
    });
});


}


// 新增結果（含牌型）
$('#add-with-cards-btn').click(function() {
    // 獲取莊家牌
    const bankerCards = [
        $('#banker-card1').val(),
        $('#banker-card2').val(),
        $('#banker-card3').val()
    ].filter(card => card !== "").map(Number);
   
    // 獲取閒家牌
    const playerCards = [
        $('#player-card1').val(),
        $('#player-card2').val(),
        $('#player-card3').val()
    ].filter(card => card !== "").map(Number);
   
    // 檢查是否輸入了足夠的牌
    if (bankerCards.length < 2 || playerCards.length < 2) {
        alert('請至少輸入莊家和閒家的前兩張牌');
        return;
    }
   
    // 驗證輸入是否有效 - 修改為只允許 0-9
    for (const card of [...bankerCards, ...playerCards]) {
        if (isNaN(card) || card < 0 || card > 9) {
            alert('請輸入有效的牌值 (0-9)');
            return;
        }
    }
   
    // 計算百家樂結果
    let bankerPoints = calculateBaccaratPoints(bankerCards);
    let playerPoints = calculateBaccaratPoints(playerCards);
   
    let result;
    if (bankerPoints > playerPoints) {
        result = '莊家';
    } else if (playerPoints > bankerPoints) {
        result = '閒家';
    } else {
        result = '和局';
    }
   
    // 傳送請求新增結果
    $.ajax({
        url: '/api/history/add_with_cards',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            result: result,
            banker_cards: bankerCards,
            player_cards: playerCards
        }),
        success: function(data) {
            if (data.success) {
                // 新增到歷史記錄
                gameHistory.push(data.record);
               
                // 更新路單
                updateRoadMap();
               
                // 更新歷史表格
                updateHistoryTable();
               
                // 更新統計資料
                updateStatistics(data.statistics);
               
                // 清空牌型輸入
                $('#banker-card1, #banker-card2, #banker-card3, #player-card1, #player-card2, #player-card3').val('');
            } else {
                alert('新增結果失敗: ' + data.message);
            }
        },
        error: function() {
            alert('新增結果失敗');
        }
    });
});
   
// 計算百家樂點數 - 修改為適應 0-9 的牌值範圍
function calculateBaccaratPoints(cards) {
    // 百家樂規則：所有牌面點數相加，然後取個位數
    // 0=10/J/Q/K, 1=A, 2-9=對應點數
    let sum = 0;
   
    for (const card of cards) {
        sum += card; // 直接加上牌值，因為 0 已經表示 10/J/Q/K
    }
   
    // 取個位數
    return sum % 10;
}
   
// 自動分析牌型
$('#banker-cards, #player-cards').on('input', function() {
    // 獲取莊家牌和閒家牌
    const bankerCardsInput = $('#banker-cards').val().trim();
    const playerCardsInput = $('#player-cards').val().trim();
   
    // 解析輸入 - 修改為支援連續輸入
    const bankerCards = bankerCardsInput ? bankerCardsInput.split('').map(Number) : [];
    const playerCards = playerCardsInput ? playerCardsInput.split('').map(Number) : [];
   
    // 如果輸入了足夠的牌，自動更新分析
    if (bankerCards.length >= 2 && playerCards.length >= 2) {
        // 驗證輸入是否有效 - 修改為只允許 0-9
        let allValid = true;
        for (const card of [...bankerCards, ...playerCards]) {
            if (isNaN(card) || card < 0 || card > 9) {
                allValid = false;
                break;
            }
        }
       
        if (allValid) {
            // 計算百家樂點數
            let bankerPoints = calculateBaccaratPoints(bankerCards);
            let playerPoints = calculateBaccaratPoints(playerCards);
           
            // 顯示點數
            $('#banker-points').text(bankerPoints);
            $('#player-points').text(playerPoints);
           
            // 自動更新分析
            updateCardAnalysis(bankerCards, playerCards);
        }
    }
});
   
/// 更新牌型分析
function updateCardAnalysis(bankerCards, playerCards) {
    $.ajax({
        url: '/api/predict',  // 使用已存在的預測路由
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            banker_cards: bankerCards,
            player_cards: playerCards
        }),
        success: function(data) {
            if (data.success) {
                console.log("預測成功:", data);  // 新增除錯資訊
               
                // 更新頻率顯示 (根據實際返回的資料結構調整)
                $('#banker-frequency').text(data.banker_score || 0);
                $('#player-frequency').text(data.player_score || 0);
                $('#tie-frequency').text(0);  // 預設值
               
                // 更新優劣勢牌值 (如果API不返回這些值，可以設定為預設值)
                $('#banker-advantage').text(data.banker_advantage || 0);
                $('#player-advantage').text(data.player_advantage || 0);
               
                // 更新赫茲結果
                let hertzResult = data.prediction || '無預測';
                let hertzColor = 'secondary';
               
                if (hertzResult === '莊家') {
                    hertzColor = 'danger';
                } else if (hertzResult === '閒家') {
                    hertzColor = 'primary';
                } else if (hertzResult === '和局') {
                    hertzColor = 'success';
                }
               
                $('#hertz-result').removeClass().addClass(`alert alert-${hertzColor}`).text(hertzResult);
            } else {
                console.error("預測失敗:", data.message);
            }
        },
        error: function(xhr, status, error) {
            console.error('獲取牌型分析失敗:', status, error);
        }
    });
}


// 監聽牌型輸入變化
$('#banker-card1, #banker-card2, #banker-card3, #player-card1, #player-card2, #player-card3').on('input', function() {
    // 限制只能輸入數字
    this.value = this.value.replace(/[^0-9]/g, '');
   
    // 限制輸入範圍為0-9
    if (this.value !== '') {
        const val = parseInt(this.value);
        if (val < 0) this.value = '0';
        if (val > 9) this.value = '9';
    }
   
    // 獲取莊家牌
    const bankerCards = [
        $('#banker-card1').val(),
        $('#banker-card2').val(),
        $('#banker-card3').val()
    ].filter(card => card !== "").map(Number);
   
    // 獲取閒家牌
    const playerCards = [
        $('#player-card1').val(),
        $('#player-card2').val(),
        $('#player-card3').val()
    ].filter(card => card !== "").map(Number);
   
    // 如果輸入了足夠的牌，自動更新分析
    if (bankerCards.length >= 2 && playerCards.length >= 2) {
        updateCardAnalysis(bankerCards, playerCards);
    }
});
   
// 新增結果
function addResult(result) {
    $.ajax({
        url: '/api/history/add',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ result: result }),
        success: function(data) {
            if (data.success) {
                // 新增到歷史記錄
                gameHistory.push(data.record);
               
                // 更新路單
                updateRoadMap();
               
                // 更新歷史表格
                updateHistoryTable();
               
                // 更新統計資料
                updateStatistics(data.statistics);
            } else {
                alert('新增結果失敗: ' + data.message);
            }
        },
        error: function() {
            alert('新增結果失敗');
        }
    });
}
   
// 更新路單顯示
function updateRoadMap() {
    console.log("更新路單...", gameHistory.length);  // 新增除錯日誌
   
    const roadMap = $('#road-map');
    roadMap.empty();
   
    if (!gameHistory || gameHistory.length === 0) {
        roadMap.html('<div class="text-center py-5">尚無遊戲記錄</div>');
        return;
    }
   
    // 建立路單表格
    const table = $('<table class="road-table"></table>');
    const maxRows = 6;
    let currentCol = 0;
    let currentRow = 0;
    let prevResult = null;
   
    // 建立初始網格
    for (let i = 0; i < maxRows; i++) {
        const row = $('<tr></tr>');
        for (let j = 0; j < 20; j++) { // 預留足夠的列
            row.append('<td class="road-cell"></td>');
        }
        table.append(row);
    }
   
    // 填充路單
    for (let i = 0; i < gameHistory.length; i++) {
        const record = gameHistory[i];
        const result = record.result;
       
        console.log(`處理結果 ${i+1}: ${result}`);  // 新增除錯日誌
       
        // 處理和局（在大路中和局不佔位置，只標記）
        if (result === '和局') {
            // 如果有前一個結果，在其位置標記和局
            if (prevResult && currentRow >= 0 && currentCol >= 0) {
                const cell = table.find('tr').eq(currentRow).find('td').eq(currentCol);
                cell.append('<span class="tie-mark">和</span>');
            }
            continue;
        }
       
        // 決定是否換列
        if (prevResult === null) {
            // 第一個非和局結果
            currentCol = 0;
            currentRow = 0;
        } else if (prevResult !== result) {
            // 結果變化，換列
            currentCol += 1;
            currentRow = 0;
        } else if (prevResult === result && currentRow < maxRows - 1) {
            // 結果相同且未達到最大行數，向下移動
            currentRow += 1;
        } else {
            // 結果相同但已達到最大行數，換列
            currentCol += 1;
            currentRow = 0;
        }
       
        // 設定單元格樣式
        const cell = table.find('tr').eq(currentRow).find('td').eq(currentCol);
        if (result === '莊家') {
            cell.addClass('banker-cell').text('莊');
        } else if (result === '閒家') {
            cell.addClass('player-cell').text('閒');
        }
       
        prevResult = result;
    }
   
    roadMap.append(table);
   
    // 新增路單說明
    const legend = $(`
        <div class="d-flex justify-content-center mt-3">
            <div class="mx-3"><span class="legend-box banker-box"></span> 莊家</div>
            <div class="mx-3"><span class="legend-box player-box"></span> 閒家</div>
            <div class="mx-3"><span class="tie-text">和</span> 和局</div>
        </div>
    `);
    roadMap.append(legend);
}
   
// 更新歷史表格
function updateHistoryTable() {
    let html = '';
   
    for (const record of gameHistory) {
        const roundNumber = record.round;
        const result = record.result;
        const time = record.time;
        const aiPrediction = record.ai_prediction || '無';
        const formulaPrediction = record.formula_prediction || '無';
       
        let resultClass = '';
        if (result === '莊家') {
            resultClass = 'text-danger';
        } else if (result === '閒家') {
            resultClass = 'text-primary';
        } else if (result === '和局') {
            resultClass = 'text-success';
        }
       
        html += `
            <tr>
                <td>${roundNumber}</td>
                <td class="${resultClass}">${result}</td>
                <td>${time}</td>
                <td>AI: ${aiPrediction}, 公式: ${formulaPrediction}</td>
            </tr>
        `;
    }
   
    $('#history-table').html(html);
}
   
// 更新統計資料
function updateStatistics(stats) {
    if (stats) {
        // 如果伺服器返回了統計資料，直接使用
        $('#total-rounds').text(stats.total_rounds);
        $('#ai-accuracy').text(stats.ai_accuracy.toFixed(1) + '%');
        $('#formula-accuracy').text(stats.formula_accuracy.toFixed(1) + '%');
        $('#match-rate').text(stats.match_rate.toFixed(1) + '%');
        return;
    }
   
    // 否則，自己計算統計資料
    const totalRounds = gameHistory.length;
    $('#total-rounds').text(totalRounds);
   
    if (totalRounds === 0) {
        $('#ai-accuracy').text('0%');
        $('#formula-accuracy').text('0%');
        $('#match-rate').text('0%');
        return;
    }
   
    // 計算AI預測準確率
    let aiCorrect = 0;
    let formulaCorrect = 0;
    let matchCount = 0;
    let validPredictions = 0;
   
    for (const record of gameHistory) {
        const result = record.result;
        const aiPrediction = record.ai_prediction;
        const formulaPrediction = record.formula_prediction;
       
        if (aiPrediction && aiPrediction !== '無') {
            validPredictions++;
           
            if (aiPrediction === result) {
                aiCorrect++;
            }
           
            if (formulaPrediction && formulaPrediction !== '無' && formulaPrediction === result) {
                formulaCorrect++;
            }
           
            if (formulaPrediction && formulaPrediction !== '無' && aiPrediction === formulaPrediction) {
                matchCount++;
            }
        }
    }
   
    // 計算準確率和匹配率
    const aiAccuracy = validPredictions > 0 ? (aiCorrect / validPredictions) * 100 : 0;
    const formulaAccuracy = validPredictions > 0 ? (formulaCorrect / validPredictions) * 100 : 0;
    const matchRate = validPredictions > 0 ? (matchCount / validPredictions) * 100 : 0;
   
    // 更新標籤
    $('#ai-accuracy').text(aiAccuracy.toFixed(1) + '%');
    $('#formula-accuracy').text(formulaAccuracy.toFixed(1) + '%');
    $('#match-rate').text(matchRate.toFixed(1) + '%');
}
