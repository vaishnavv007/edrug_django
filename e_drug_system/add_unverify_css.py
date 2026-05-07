import os
os.chdir(r'd:\EDRUG\e_drug_system')
with open('static/css/style.css', 'a') as f:
    css = '''
/* Unverify Button */
.btn-unverify {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: #fff;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    font-size: 0.95rem;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-unverify:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}
'''
    f.write(css)
print('Unverify button CSS added')
