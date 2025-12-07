/*
 This file is part of TrollVNC
 Copyright (c) 2025 82Flex <82flex@gmail.com> and contributors

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License version 2
 as published by the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
*/

#import "TVNCMainViewController.h"
#import "TVNCServiceCoordinator.h"
#import <UserNotifications/UserNotifications.h>
#import <signal.h>
#import <sys/sysctl.h>
#import <dlfcn.h>
#import <string.h>

@interface TVNCMainViewController ()

@property (nonatomic, strong) UITextField *serverTextField;
@property (nonatomic, strong) UISwitch *enableSwitch;
@property (nonatomic, strong) UILabel *statusLabel;
@property (nonatomic, strong) UIButton *applyButton;
@property (nonatomic, strong) NSUserDefaults *defaults;

@end

@implementation TVNCMainViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.defaults = [[NSUserDefaults alloc] initWithSuiteName:@"com.82flex.trollvnc"];
    
    [self setupUI];
    [self loadSettings];
    [self updateStatus];
    
    [[NSNotificationCenter defaultCenter] addObserver:self
                                             selector:@selector(serviceStatusDidChange:)
                                                 name:TVNCServiceStatusDidChangeNotification
                                               object:nil];
}

- (void)setupUI {
    self.view.backgroundColor = [UIColor systemBackgroundColor];
    self.title = @"TrollVNC";
    
    // Server Domain:Port Text Field
    UILabel *serverLabel = [[UILabel alloc] init];
    serverLabel.text = @"Server Domain (Domain:Port)";
    serverLabel.font = [UIFont systemFontOfSize:16 weight:UIFontWeightMedium];
    serverLabel.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:serverLabel];
    
    UILabel *serverHint = [[UILabel alloc] init];
    serverHint.text = @"✅ Khuyến nghị: Dùng domain (ví dụ: serverapi.xyz:10010)\n⚠️ IP thay đổi liên tục nên không ổn định";
    serverHint.font = [UIFont systemFontOfSize:12];
    serverHint.textColor = [UIColor systemOrangeColor];
    serverHint.numberOfLines = 0;
    serverHint.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:serverHint];
    
    self.serverTextField = [[UITextField alloc] init];
    self.serverTextField.placeholder = @"serverapi.xyz:10010";
    self.serverTextField.borderStyle = UITextBorderStyleRoundedRect;
    self.serverTextField.keyboardType = UIKeyboardTypeURL;
    self.serverTextField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    self.serverTextField.autocorrectionType = UITextAutocorrectionTypeNo;
    self.serverTextField.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:self.serverTextField];
    
    // Enable/Disable Switch
    UILabel *enableLabel = [[UILabel alloc] init];
    enableLabel.text = @"Enable Reverse Connection";
    enableLabel.font = [UIFont systemFontOfSize:16 weight:UIFontWeightMedium];
    enableLabel.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:enableLabel];
    
    self.enableSwitch = [[UISwitch alloc] init];
    self.enableSwitch.onTintColor = [UIColor systemBlueColor];
    [self.enableSwitch addTarget:self action:@selector(switchChanged:) forControlEvents:UIControlEventValueChanged];
    self.enableSwitch.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:self.enableSwitch];
    
    // Status Label
    self.statusLabel = [[UILabel alloc] init];
    self.statusLabel.text = @"Status: Stopped";
    self.statusLabel.font = [UIFont systemFontOfSize:14];
    self.statusLabel.textColor = [UIColor secondaryLabelColor];
    self.statusLabel.textAlignment = NSTextAlignmentCenter;
    self.statusLabel.numberOfLines = 0;
    self.statusLabel.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:self.statusLabel];
    
    // Apply Button
    self.applyButton = [UIButton buttonWithType:UIButtonTypeSystem];
    [self.applyButton setTitle:@"Apply & Restart" forState:UIControlStateNormal];
    self.applyButton.titleLabel.font = [UIFont systemFontOfSize:18 weight:UIFontWeightSemibold];
    self.applyButton.backgroundColor = [UIColor systemBlueColor];
    [self.applyButton setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
    self.applyButton.layer.cornerRadius = 10;
    [self.applyButton addTarget:self action:@selector(applyChanges) forControlEvents:UIControlEventTouchUpInside];
    self.applyButton.translatesAutoresizingMaskIntoConstraints = NO;
    [self.view addSubview:self.applyButton];
    
    // Layout Constraints
    [NSLayoutConstraint activateConstraints:@[
        // Server Label
        [serverLabel.topAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.topAnchor constant:40],
        [serverLabel.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        [serverLabel.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        
        // Server Hint
        [serverHint.topAnchor constraintEqualToAnchor:serverLabel.bottomAnchor constant:5],
        [serverHint.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        [serverHint.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        
        // Server Text Field
        [self.serverTextField.topAnchor constraintEqualToAnchor:serverHint.bottomAnchor constant:10],
        [self.serverTextField.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        [self.serverTextField.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        [self.serverTextField.heightAnchor constraintEqualToConstant:44],
        
        // Enable Label
        [enableLabel.topAnchor constraintEqualToAnchor:self.serverTextField.bottomAnchor constant:30],
        [enableLabel.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        
        // Enable Switch
        [self.enableSwitch.centerYAnchor constraintEqualToAnchor:enableLabel.centerYAnchor],
        [self.enableSwitch.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        
        // Status Label
        [self.statusLabel.topAnchor constraintEqualToAnchor:enableLabel.bottomAnchor constant:30],
        [self.statusLabel.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        [self.statusLabel.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        
        // Apply Button
        [self.applyButton.topAnchor constraintEqualToAnchor:self.statusLabel.bottomAnchor constant:40],
        [self.applyButton.leadingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.leadingAnchor constant:20],
        [self.applyButton.trailingAnchor constraintEqualToAnchor:self.view.safeAreaLayoutGuide.trailingAnchor constant:-20],
        [self.applyButton.heightAnchor constraintEqualToConstant:50],
    ]];
}

- (void)loadSettings {
    NSString *reverseSocket = [self.defaults stringForKey:@"ReverseSocket"];
    if (reverseSocket) {
        self.serverTextField.text = reverseSocket;
    }
    
    NSString *reverseMode = [self.defaults stringForKey:@"ReverseMode"];
    BOOL isEnabled = reverseMode && ![reverseMode isEqualToString:@"none"];
    self.enableSwitch.on = isEnabled;
}

- (void)switchChanged:(UISwitch *)sender {
    // Update UI immediately
    [self updateStatus];
}

- (void)updateStatus {
    BOOL isEnabled = self.enableSwitch.on;
    BOOL isRunning = [[TVNCServiceCoordinator sharedCoordinator] isServiceRunning];
    
    if (isEnabled && isRunning) {
        self.statusLabel.text = @"Status: Running";
        self.statusLabel.textColor = [UIColor systemGreenColor];
    } else if (isEnabled && !isRunning) {
        self.statusLabel.text = @"Status: Enabled (Starting...)";
        self.statusLabel.textColor = [UIColor systemOrangeColor];
    } else {
        self.statusLabel.text = @"Status: Disabled";
        self.statusLabel.textColor = [UIColor secondaryLabelColor];
    }
}

- (void)serviceStatusDidChange:(NSNotification *)notification {
    dispatch_async(dispatch_get_main_queue(), ^{
        [self updateStatus];
    });
}

- (void)applyChanges {
    [self.view endEditing:YES];
    
    // Validate input
    NSString *serverText = [self.serverTextField.text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    BOOL isEnabled = self.enableSwitch.on;
    
    if (isEnabled && (!serverText || serverText.length == 0)) {
        UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Thiếu thông tin"
                                                                       message:@"Vui lòng nhập domain:port (ví dụ: serverapi.xyz:10010)"
                                                                preferredStyle:UIAlertControllerStyleAlert];
        [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleCancel handler:nil]];
        [self presentViewController:alert animated:YES completion:nil];
        return;
    }
    
    // Validate Domain:Port format (prefer domain over IP)
    if (isEnabled) {
        NSArray *components = [serverText componentsSeparatedByString:@":"];
        if (components.count != 2) {
            UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Định dạng không hợp lệ"
                                                                           message:@"Vui lòng nhập theo định dạng: Domain:Port\n\nVí dụ:\n- serverapi.xyz:10010\n- myserver.com:10050"
                                                                    preferredStyle:UIAlertControllerStyleAlert];
            [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleCancel handler:nil]];
            [self presentViewController:alert animated:YES completion:nil];
            return;
        }
        
        NSString *host = components[0];
        NSString *portStr = components[1];
        
        // Validate host (prefer domain, warn if IP)
        if (host.length == 0) {
            UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Thiếu Domain"
                                                                           message:@"Vui lòng nhập domain (ví dụ: serverapi.xyz)"
                                                                    preferredStyle:UIAlertControllerStyleAlert];
            [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleCancel handler:nil]];
            [self presentViewController:alert animated:YES completion:nil];
            return;
        }
        
        // Check if input is IP address (contains only numbers and dots)
        NSCharacterSet *ipCharacterSet = [NSCharacterSet characterSetWithCharactersInString:@"0123456789."];
        NSCharacterSet *hostCharacterSet = [NSCharacterSet characterSetWithCharactersInString:host];
        BOOL isIP = [hostCharacterSet isSubsetOfSet:ipCharacterSet] && [host containsString:@"."];
        
        if (isIP) {
            // Warn user about IP instability
            UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"⚠️ Cảnh báo: Đang dùng IP"
                                                                           message:@"IP thay đổi liên tục sẽ làm mất kết nối!\n\nKhuyến nghị: Dùng domain thay vì IP\n\nVí dụ: serverapi.xyz:10010\n\nBạn có muốn tiếp tục với IP không?"
                                                                    preferredStyle:UIAlertControllerStyleAlert];
            [alert addAction:[UIAlertAction actionWithTitle:@"Hủy" style:UIAlertActionStyleCancel handler:nil]];
            __weak typeof(self) weakSelf = self;
            [alert addAction:[UIAlertAction actionWithTitle:@"Tiếp tục với IP"
                                                      style:UIAlertActionStyleDefault
                                                    handler:^(UIAlertAction *action) {
                                                        [weakSelf proceedWithConnection:serverText];
                                                    }]];
            [self presentViewController:alert animated:YES completion:nil];
            return;
        }
        
        // Validate port
        int port = [portStr intValue];
        if (port < 10001 || port > 10500) {
            UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Port không hợp lệ"
                                                                           message:@"Port phải từ 10001 đến 10500"
                                                                    preferredStyle:UIAlertControllerStyleAlert];
            [alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleCancel handler:nil]];
            [self presentViewController:alert animated:YES completion:nil];
            return;
        }
        
        // Proceed with domain connection
        [self proceedWithConnection:serverText];
    }
}

- (void)proceedWithConnection:(NSString *)serverText {
    // Save settings
    BOOL isEnabled = self.enableSwitch.on;
    
    if (isEnabled) {
        [self.defaults setObject:serverText forKey:@"ReverseSocket"];
        [self.defaults setObject:@"viewer" forKey:@"ReverseMode"];
    } else {
        [self.defaults setObject:@"none" forKey:@"ReverseMode"];
    }
    [self.defaults synchronize];
    
    // Show confirmation
    NSString *title = @"Áp dụng thay đổi";
    NSString *message = isEnabled ? 
        [NSString stringWithFormat:@"Server: %@\n\nKhởi động lại VNC service?", serverText] :
        @"Tắt reverse connection và khởi động lại VNC service?";
    
    UIAlertController *alert = [UIAlertController alertControllerWithTitle:title
                                                                   message:message
                                                            preferredStyle:UIAlertControllerStyleAlert];
    [alert addAction:[UIAlertAction actionWithTitle:@"Hủy" style:UIAlertActionStyleCancel handler:nil]];
    __weak typeof(self) weakSelf = self;
    [alert addAction:[UIAlertAction actionWithTitle:@"Khởi động lại"
                                              style:UIAlertActionStyleDestructive
                                            handler:^(UIAlertAction *action) {
                                                [weakSelf restartService];
                                            }]];
    
    [self presentViewController:alert animated:YES completion:nil];
}

// Helper function to restart VNC service
static void TVNCRestartVNCService(void) {
    // Enumerate processes to find trollvncserver
    size_t procInfoLength = 0;
    if (sysctl((int[]){CTL_KERN, KERN_PROC, KERN_PROC_ALL, 0}, 4, NULL, &procInfoLength, NULL, 0) < 0) {
        return;
    }
    
    struct kinfo_proc *procInfo = (struct kinfo_proc *)calloc(1, procInfoLength + 1);
    if (!procInfo) return;
    if (sysctl((int[]){CTL_KERN, KERN_PROC, KERN_PROC_ALL, 0}, 4, procInfo, &procInfoLength, NULL, 0) < 0) {
        free(procInfo);
        return;
    }
    
    int procInfoCnt = (int)(procInfoLength / sizeof(struct kinfo_proc));
    for (int i = 0; i < procInfoCnt; i++) {
        pid_t pid = procInfo[i].kp_proc.p_pid;
        if (pid <= 1) continue;
        
        size_t argSize = 4096;
        char *argBuffer = (char *)calloc(1, argSize + 1);
        if (!argBuffer) continue;
        
        if (sysctl((int[]){CTL_KERN, KERN_PROCARGS2, pid, 0}, 4, NULL, &argSize, NULL, 0) < 0) {
            free(argBuffer);
            continue;
        }
        
        memset(argBuffer, 0, argSize + 1);
        if (sysctl((int[]){CTL_KERN, KERN_PROCARGS2, pid, 0}, 4, argBuffer, &argSize, NULL, 0) < 0) {
            free(argBuffer);
            continue;
        }
        
        NSString *exePath = [NSString stringWithUTF8String:(argBuffer + sizeof(int))] ?: @"";
        if ([exePath.lastPathComponent isEqualToString:@"trollvncserver"]) {
            kill(pid, SIGTERM);
            free(argBuffer);
            break;
        }
        free(argBuffer);
    }
    free(procInfo);
}

- (void)restartService {
    // Restart VNC service
    TVNCRestartVNCService();
    
    // Update status after a delay
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(1.0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        [self updateStatus];
    });
}

- (void)dealloc {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
}

@end

